import pymysql

class Database:
    def __init__(self, host, port, user, password, db):
        self.conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db)
        self.cur = self.conn.cursor()

    def insert(self,DATETIME,TYPE,X,Y,Z,U,V,W):
        #self.cur.execute("INSERT INTO sbls ( DATETIME,TYPE,X,Y,Z,U,V,W) VALUES ( %s,%s,%s,%s,%s,%s,%s,%s)", (DATETIME,TYPE,X,Y,Z,U,V,W))
        self.conn.commit()

    def view(self):
        self.cur.execute("SELECT * FROM records")
        rows = self.cur.fetchall()
        return rows

    def search(self, name="", age="", email=""):
        self.cur.execute("SELECT * FROM records WHERE name=%s OR age=%s OR email=%s", (name, age, email))
        rows = self.cur.fetchall()
        return rows

    
    def search2(self):
        self.cur.execute("SELECT * FROM sbls WHERE ID IN (SELECT MAX(ID) FROM sbls)")
        rows = self.cur.fetchall()
        return rows

    def delete(self, id):
        self.cur.execute("DELETE FROM records WHERE id=%s", (id,))
        self.conn.commit()

    def update(self, id, name, age, email):
        self.cur.execute("UPDATE records SET name=%s, age=%s, email=%s WHERE id=%s", (name, age, email, id))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

#if __name__ == '__main__':
#    host = 'localhost'
#    port = 3306
#    password = 'JYZN_2331_agv'
#    db = 'gad'
#    user = 'root'
#    Database = Database(host, port, user,password, db)
#    Database.insert(1,2,3,4)