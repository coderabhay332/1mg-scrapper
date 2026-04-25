import csv

input_file = 'drugs_urls.csv'
hindi_output = 'hindi_drugs_urls.csv'
english_output = 'english_drugs_urls.csv'

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(hindi_output, 'w', newline='', encoding='utf-8') as hindi_file, \
     open(english_output, 'w', newline='', encoding='utf-8') as english_file:

    hindi_writer = csv.writer(hindi_file)
    english_writer = csv.writer(english_file)

    for line in infile:
        url = line.strip()
        if '/hi/drugs/' in url:
            english_writer.writerow([url])
        else:
            hindi_writer.writerow([url])

print(f"Split complete!")
print(f"Hindi URLs saved to: {hindi_output}")
print(f"English URLs saved to: {english_output}")
