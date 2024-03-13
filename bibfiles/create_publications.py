import os
import re
from pybtex.database.input import bibtex
import html

section_titles = {
    "sec:preprints": "Preprints",
    "sec:books": "Books",
    "sec:proceedings": "Proceedings and Book Chapters",
    "sec:journalpapers": "Journal Papers",
    "sec:theses": "Theses",
}

def latex_to_unicode(text):
    mappings = {
        "\\'{e}": "é", "\\~{u}": "ũ", "\\`{e}": "è",
        # Add more mappings as needed
    }
    regex = re.compile('|'.join(re.escape(key) for key in mappings.keys()))
    return regex.sub(lambda m: mappings[m.group()], text)

def clean_bibtex_string(value):
    value = latex_to_unicode(value)    
    value = re.sub(r'{|}', '', value)
    return html.escape(value)

def format_author_name(person):
    first = ' '.join(person.bibtex_first_names)
    last = ' '.join(person.last_names)
    full_name = f"{first} {last}"
    return clean_bibtex_string(full_name)

def format_authors(entry):
    authors = [format_author_name(person) for person in entry.persons.get('author', [])]
    if len(authors) > 2:
        return ', '.join(authors[:-1]) + ', and ' + authors[-1]
    return ' and '.join(authors)

def get_publication_info(entry):
    if entry.type == 'phdthesis':
        return "PhD thesis"
    elif entry.type == 'mastersthesis':
        return "Master's thesis"
    else:
        journal = entry.fields.get('journal', '')
        if not journal:
            journal = entry.fields.get('publisher', '')
        return clean_bibtex_string(journal)

def parse_bib_file(bib_file):
    parser = bibtex.Parser()
    return parser.parse_file(bib_file)

def generate_individual_html(entry, output_dir, title, key):
    bibtex_content = html.escape(entry.to_string('bibtex'))
    html_content = f"""---
layout: archive
title: "{title}"
permalink: /{key}.html
---

<pre>
{bibtex_content}
</pre>
"""
    with open(os.path.join(output_dir, f"{key}.html"), 'w') as html_file:
        html_file.write(html_content)


def escape_for_html_attribute(js_string):
    """
    Prepares a JavaScript string to be placed inside an HTML attribute.
    The function replaces quotes with their HTML entity equivalents.
    """
    return js_string.replace('"', '&quot;').replace("'", '&#39;')

def generate_bibtex_entry_button_with_curly_brackets(bibtex_entry):
    """
    Generates a JavaScript snippet for copying the BibTeX entry, modifying it
    to use curly brackets instead of quotes for field values. This version also
    ensures proper handling of line breaks and HTML attribute escaping.
    """
    # Convert the BibTeX entry to string
    bibtex_string = bibtex_entry.to_string('bibtex')
    
    # Replace double quotes with curly brackets for field values, ensuring proper JavaScript handling
    # Note: This simple replacement assumes the BibTeX fields do not contain nested curly brackets.
    bibtex_string_with_curly_brackets = re.sub(r'=\s*"([^"]*)"', r'= {\1}', bibtex_string)
    
    # Escape for HTML attribute and replace line breaks for HTML/JS compatibility
    escaped_bibtex_string = escape_for_html_attribute(bibtex_string_with_curly_brackets).replace('\n', '\\n')
    
    # Generate the HTML for the copy button with the formatted BibTeX string
    button_html = f"""<button onclick='copyToClipboard("{escaped_bibtex_string}")' style='padding:0px; background-color:#f0f0f0;border:1px solid #ccc;cursor:pointer;border-radius:5px;'>copy</button>"""
    return button_html

def generate_bibtex_entry_button(bibtex_entry):
    """
    Generates a JavaScript snippet for copying the BibTeX entry, with modifications
    to handle line breaks and ensure correct JavaScript string formatting.
    """
    # Convert the BibTeX entry to string and prepare it for HTML attribute inclusion
    bibtex_string = bibtex_entry.to_string('bibtex')
    # Escape quotes and replace line breaks to ensure the string is handled correctly in HTML/JS
    escaped_bibtex_string = escape_for_html_attribute(bibtex_string).replace('\n', '\\n')
    
    # Generate the HTML for the copy button with the properly formatted BibTeX string
    button_html = f"""<button onclick='copyToClipboard("{escaped_bibtex_string}")' style='padding:0px;background-color:#f0f0f0;border:1px solid #ccc;cursor:pointer;'>copy</button>"""
    return button_html
        
def generate_publications_md_and_html_files(bib_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    md_content = """---
title: Publications
permalink: /publications/
layout: archive
---

<script>
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Copying bibtex entry to clipboard was successful!');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}
</script>

"""

    current_section_opened = False
    for entry in bib_data.entries.values():
        if entry.type == 'section':
            if current_section_opened:
                md_content += "</ul>\n"
            section_key = entry.key.lower()
            section_title = section_titles.get(section_key, "Other")
            md_content += f"\n<h2>{section_title}</h2>\n<ul class=\"my-publication-list\">\n"
            current_section_opened = True
        else:
            authors = format_authors(entry)
            title = clean_bibtex_string(entry.fields.get('title', 'No Title'))
            year = entry.fields.get('year', 'No Year')
            publication_info = get_publication_info(entry)
            url = entry.fields.get('url', entry.fields.get('eprint', '#'))
            key = entry.key

            bibtex_string_for_js = html.escape(entry.to_string('bibtex').replace('"', '&quot;'))
            
            md_content += f"""<li><b>{title}</b><br />
{year}{f" - {publication_info}" if publication_info else ""}<br>
{authors}<br>
<a href="{url}">link</a>, <a href="/{key}.html">bibtex</a>"""
            bibtex_copy_button = generate_bibtex_entry_button_with_curly_brackets(entry)
            md_content += " "+bibtex_copy_button+f"</li>\n"
            generate_individual_html(entry, output_dir, title, key)

    if current_section_opened:
        md_content += "</ul>\n"

    md_content += """
<script>
    window.onload = function() {
        let count = 0;
        const lists = document.getElementsByClassName('my-publication-list');

        for (let list of lists) {
            const items = list.getElementsByTagName('li');
            count += items.length;
        }
        count -= 2; // Subtract 2 for the last two theses

        // Enumerate items in reverse
        for (let list of lists) {
            const items = list.getElementsByTagName('li');
            for (let item of items) {
                if (count > 0) {
                    item.innerHTML = `<b>[${count}]</b> ` + item.innerHTML;
                }
                count--;
            }
        }
    }
</script>
"""

    with open(os.path.join(output_dir, "publications.md"), 'w') as md_file:
        md_file.write(md_content)

def main(bib_file, output_dir):
    bib_data = parse_bib_file(bib_file)
    generate_publications_md_and_html_files(bib_data, output_dir)
    print("Done generating publications.md and HTML files with copy functionality.")

bib_file = './main.bib'  # Path to your BibTeX file
output_dir = '.'  # Output directory for the HTML files and publications.md

main(bib_file, output_dir)
