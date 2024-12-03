import sqlite3

def main():
    connection = sqlite3.connect('agricolaif.db')

    with open('schema.sql') as f:
        connection.execute(f.read())

    connection.close()

if __name__ == "__main__":
    main()