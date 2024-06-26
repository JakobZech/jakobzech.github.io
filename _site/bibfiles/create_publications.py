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
    # LaTeX to Unicode mappings, add more mappings as needed
    mappings = {
        "\\'{e}": "é", "\\~{u}": "ũ", "\\`{e}": "è",
        "\\$": "$",  # Preserve $ for LaTeX math
    }
    # Preserve LaTeX math by temporarily replacing it
    math_regex = re.compile(r'(\$\$?.*?\$\$?)')
    math_matches = math_regex.findall(text)
    text = math_regex.sub('MATH_PLACEHOLDER', text)
    
    regex = re.compile('|'.join(re.escape(key) for key in mappings.keys()))
    text = regex.sub(lambda m: mappings[m.group()], text)

    # Restore LaTeX math
    for match in math_matches:
        text = text.replace('MATH_PLACEHOLDER', match, 1)
    
    return text

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
        return ', '.join(authors[:-1]) + ' and ' + authors[-1]
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
    # Convert the BibTeX entry to a string
    bibtex_content = entry.to_string('bibtex')
    
    # Replace quotes around field values with curly brackets
    bibtex_content_with_curly_brackets = re.sub(r'=\s*"([^"]*)"', r'= {\1}', bibtex_content)
    
    # Prepare the BibTeX string for inclusion in an HTML attribute
    bibtex_content_for_html_attribute = html.escape(bibtex_content_with_curly_brackets).replace('"', '&quot;')
    
    # Generate the HTML content with a copy button
    html_content = f"""---
layout: archive
title: "{title}"
permalink: /publications/{key}.html
---

<script>
function copyToClipboard() {{
    const el = document.createElement('textarea');
    el.value = `{bibtex_content_with_curly_brackets}`;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    alert('BibTeX entry copied to clipboard!');
}}
</script>

<button onclick='copyToClipboard()' style='padding:5px; background-color:#f0f0f0;border:1px solid #ccc;cursor:pointer;border-radius:5px;'>Copy BibTeX</button>

<pre>
{html.escape(bibtex_content_with_curly_brackets)}
</pre>
"""
    with open(os.path.join(output_dir, f"{key}.html"), 'w') as html_file:
        html_file.write(html_content)

# def generate_individual_html(entry, output_dir, title, key):
#     # Convert the BibTeX entry to a string
#     bibtex_content = entry.to_string('bibtex')
    
#     # Replace quotes around field values with curly brackets
#     bibtex_content_with_curly_brackets = re.sub(r'=\s*"([^"]*)"', r'= {\1}', bibtex_content)
    
#     # Escape the modified BibTeX string for HTML
#     bibtex_content_escaped = html.escape(bibtex_content_with_curly_brackets)
    
#     html_content = f"""---
# layout: archive
# title: "{title}"
# permalink: /publications/{key}.html
# ---

# <pre>
# {bibtex_content_escaped}
# </pre>
# """
#     with open(os.path.join(output_dir, f"{key}.html"), 'w') as html_file:
#         html_file.write(html_content)

def escape_for_html_attribute(js_string):
    return js_string.replace('"', '&quot;').replace("'", '&#39;')

def generate_bibtex_entry_button_with_curly_brackets(bibtex_entry):
    bibtex_string = bibtex_entry.to_string('bibtex')
    bibtex_string_with_curly_brackets = re.sub(r'=\s*"([^"]*)"', r'= {\1}', bibtex_string)
    escaped_bibtex_string = escape_for_html_attribute(bibtex_string_with_curly_brackets).replace('\n', '\\n')
    button_html = f"""<button onclick='copyToClipboard("{escaped_bibtex_string}")' style='padding:0px; background-color:#f0f0f0;border:1px solid #ccc;cursor:pointer;border-radius:5px;'>copy</button>"""
    return button_html

def generate_bibtex_entry_button(bibtex_entry):
    bibtex_string = bibtex_entry.to_string('bibtex')
    escaped_bibtex_string = escape_for_html_attribute(bibtex_string).replace('\n', '\\n')
    button_html = f"""<button onclick='copyToClipboard("{escaped_bibtex_string}")' style='padding:0px;background-color:#f0f0f0;border:1px solid #ccc;cursor:pointer;'>copy</button>"""
    return button_html
        
def generate_publications_md_and_html_files(bib_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    md_content = """---
title: Publications
permalink: /publications/
layout: archive
---

<script type="text/javascript" async
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
</script>

<script>
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('BibTeX entry copied to clipboard!');
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

            md_content += f"""<li><b>{title}</b><br />
<i>{publication_info}</i>, {year}<br>
{authors}<br>
<a href="{url}">Link</a>, <a href="/publications/{key}.html">BibTex</a>"""
            bibtex_copy_button = generate_bibtex_entry_button_with_curly_brackets(entry)
            md_content += " "+bibtex_copy_button+f"</li>\n"
            generate_individual_html(entry, output_dir, title, key)

    if current_section_opened:
        md_content += "</ul>\n"

    md_content += '<a href="/files/main.bib" download="main.bib" style="padding:0px;background-color:#f0f0f0;border:1px solid #ccc;cursor:pointer;border-radius:5px;display:inline-block;text-decoration:none;color:black;">Download main.bib</a>\n'
    # md_content += '<button href="/files/main.bib" download="main.bib" style="padding:0px;background-color:#f0f0f0;border:1px solid #ccc;cursor:pointer;border-radius:5px">Download main.bib</button>\n'
        
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

def filter_and_save(input_filepath, output_filepath):
    try:
        with open(input_filepath, 'r') as file:
            lines = file.readlines()

        filtered_lines = [line for line in lines if "@Section" not in line]

        with open(output_filepath, 'w') as file:
            file.writelines(filtered_lines)
            
        print("File processed and saved successfully.")

    except FileNotFoundError:
        print("Error: The file at the specified input filepath does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def main(bib_file, output_dir):
    filter_and_save(bib_file,bib_file_download)    
    bib_data = parse_bib_file(bib_file)
    generate_publications_md_and_html_files(bib_data, output_dir)
    print("Done generating publications.md and HTML files with copy functionality.")

bib_file = './main.bib'  # Path to your BibTeX file
bib_file_download = '../files/main.bib'  # Path to your BibTeX file
output_dir = '.'  # Output directory for the HTML files and publications.md

main(bib_file, output_dir)
