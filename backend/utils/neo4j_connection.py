from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            return session.run(query, parameters).data()

if __name__ == "__main__":
    conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", password="#Sandipan55")
    result = conn.query("RETURN 'Neo4j is connected!' AS message")
    print(result)
    conn.close()
