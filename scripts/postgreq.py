import psycopg2

try:
    conn = psycopg2.connect("dbname='musicbrainz' user='musicbrainz' host='139.162.16.218' password='mbrainz'")

except IOError as e :
    print "I am unable to connect to the database" + e


cur = conn.cursor()
cur.execute("""SELECT * from artist limit 10""")

colnames = [desc[0] for desc in cur.description]

rows = cur.fetchall()

print "\nShow me the databases:\n"
print colnames
for row in rows:
    print "   ", row
