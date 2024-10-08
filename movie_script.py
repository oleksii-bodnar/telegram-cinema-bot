import csv

movies = {}

with open('title.basics.tsv', 'r', encoding='utf-8') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter='\t')
    for row in reader:
        if row['titleType'] == 'movie' and row['isAdult'] == '0':
            title = row['primaryTitle']
            description = f"Рік випуску: {row['startYear']}, Жанр: {row['genres']}"
            movies[title] = description

            if len(movies) >= 100:
                break

with open('movies.txt', 'w', encoding='utf-8') as file:
    for title, description in movies.items():
        file.write(f"{title}|{description}\n")