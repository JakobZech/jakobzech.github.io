import os
from pybtex.database.input import bibtex

# The path to your .bib file
bib_file = './main.bib'

# The directory where you want to save the HTML files, ideally inside your Jekyll project
output_dir = '.'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Function to create HTML content with Jekyll front matter from BibTeX entry
def create_html_content(entry_key, entry):
    # Use the BibTeX entry key for the URL/permalink
    permalink = f"/publications/bibtex/{entry_key}/"

    return f"""---
layout: page
title: "{entry.fields['title']}"
permalink: {permalink}
---

<pre>
{entry.to_string('bibtex')}
</pre>
"""

# Parse the BibTeX file
parser = bibtex.Parser()
bib_data = parser.parse_file(bib_file)

# Loop over each entry in the BibTeX file
for key, entry in bib_data.entries.items():
    # Generate the HTML content for the entry, including Jekyll front matter
    # Pass the entry key as an argument to the create_html_content function
    html_content = create_html_content(key, entry)
    
    # Define the output file name, using the entry key
    output_file_path = os.path.join(output_dir, f"{key}.html")
    
    # Write the HTML content to the file
    with open(output_file_path, 'w') as html_file:
        html_file.write(html_content)

print("HTML files with Jekyll front matter have been generated.")
