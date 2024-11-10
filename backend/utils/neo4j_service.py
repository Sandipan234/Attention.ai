from neo4j import GraphDatabase

class DynamicPreferenceUpdater:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the database connection."""
        self.driver.close()

    def get_user_data(self, user_id):
        """
        Fetch existing user data from the database.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            dict: User's budget, location, and preferences.
        """
        query = """
        MATCH (u:User {id: $userId})-[:HAS_PREFERENCE]->(p:Preference)
        RETURN u.budget AS budget, u.location AS location, 
               COLLECT({type: p.type, intensity: p.intensity}) AS preferences
        """
        with self.driver.session() as session:
            result = session.run(query, userId=user_id).single()
            if result:
                return {
                    "budget": result["budget"] or "unknown",
                    "location": result["location"] or "unknown",
                    "preferences": result["preferences"] or []
                }
            return {"budget": "unknown", "location": "unknown", "preferences": []}

    def update_user_data(self, user_id, new_data):
        """
        Merge new data into the existing user profile.

        Args:
            user_id (str): Unique identifier for the user.
            new_data (dict): New data to update, including budget, location, and preferences.

        Returns:
            dict: Updated user data.
        """
        # Fetch previous data
        previous_data = self.get_user_data(user_id)

        # Merge fields
        budget = new_data.get("budget", previous_data["budget"])
        location = new_data.get("location", previous_data["location"])
        new_preferences = new_data.get("preferences", [])

        # Merge preferences dynamically
        merged_preferences = {p["type"]: p["intensity"] for p in previous_data["preferences"]}
        for pref in new_preferences:
            merged_preferences[pref["type"]] = pref["intensity"]

        # Format preferences for saving
        formatted_preferences = [{"type": k, "intensity": v} for k, v in merged_preferences.items()]

        query = """
        MERGE (u:User {id: $userId})
        ON CREATE SET u.budget = $budget, u.location = $location
        ON MATCH SET u.budget = $budget, u.location = $location
        WITH u
        UNWIND $preferences AS pref
        MERGE (p:Preference {type: pref.type})
        ON CREATE SET p.intensity = pref.intensity
        ON MATCH SET p.intensity = pref.intensity
        MERGE (u)-[:HAS_PREFERENCE]->(p)
        """
        with self.driver.session() as session:
            session.run(
                query, userId=user_id, budget=budget, location=location, preferences=formatted_preferences
            )
        return {"user_id": user_id, "budget": budget, "location": location, "preferences": formatted_preferences}

    def save_user_data_with_context(self, user_id, location, preferences):
        """
        Save user preferences with contextual locations to Neo4j.

        Args:
            user_id (str): Unique identifier for the user.
            location (str): Location for which preferences are being specified.
            preferences (list): List of preferences with type and intensity.
        """
        # Fetch the most recent valid location if the current location is None
        if location is None:
            location_query = """
            MATCH (u:User {id: $userId})-[:HAS_LOCATION]->(loc:Location)
            RETURN loc.name AS last_location
            ORDER BY loc.timestamp DESC
            LIMIT 1
            """
            with self.driver.session() as session:
                last_location_result = session.run(location_query, userId=user_id).single()
                location = last_location_result["last_location"] if last_location_result else None

        # If location is still None, skip saving location
        if location is None:
            raise ValueError("Cannot save preferences without a valid location.")

        # Save preferences with the valid location
        query = """
        MERGE (u:User {id: $userId})
        MERGE (loc:Location {name: $location})
        MERGE (u)-[:HAS_LOCATION]->(loc)
        WITH loc
        UNWIND $preferences AS pref
        MERGE (p:Preference {type: pref.type})
        ON CREATE SET p.intensity = pref.intensity
        ON MATCH SET p.intensity = COALESCE(pref.intensity, p.intensity)
        MERGE (loc)-[:HAS_PREFERENCE]->(p)
        """
        with self.driver.session() as session:
            session.run(query, userId=user_id, location=location, preferences=preferences)


    def get_contextual_data(self, user_id):
        """
        Fetch user preferences and their associated locations.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            list: User's contextual preferences mapped to locations.
        """
        query = """
        MATCH (u:User {id: $userId})-[:HAS_LOCATION]->(loc:Location)
        OPTIONAL MATCH (loc)-[:HAS_PREFERENCE]->(p:Preference)
        RETURN loc.name AS location, COLLECT({type: p.type, intensity: p.intensity}) AS preferences
        """
        with self.driver.session() as session:
            results = session.run(query, userId=user_id)
            data = []
            for record in results:
                data.append({
                    "location": record["location"],
                    "preferences": record["preferences"] or []
                })
            return data
