try:
    from utils import *
except ImportError:
    from scrapeutils.utils import *

SCRIPTPATH=os.path.dirname(os.path.abspath(sys.argv[0]))
JSON_OUTPUT_FILE = os.path.abspath(os.path.join(SCRIPTPATH, '..', "data", "courses.json"))
SEARCH_URL = r'https://www.pluralsight.com/search?categories=course&sort=title'


def main():
    course_dict = load_stored_json(JSON_OUTPUT_FILE)
    source_data = get_courselist_source(SEARCH_URL, n_pages=500)

    class_name = r'search-result columns'
    search_snippets = outer_search_html(source_data, class_name)
    
    title_tag=r'<div class="search-result__title">'
    author_tag=r'<div class="search-result__author">'
    level_tag=r'<div class="search-result__level">'
    date_tag=r'<div class="search-result__date">'
    length_tag=r'<div class="search-result__length show-for-large-up">'
    div_tag=r'</div>'; quote = r'"'; gt = r'>'; a_tag = r'</a>'; href=r'href="'

    title_lookaround = lookaround_tags(title_tag, div_tag)
    author_lookaround = lookaround_tags(author_tag, div_tag)
    level_lookaround = lookaround_tags(level_tag, div_tag)
    date_lookaround = lookaround_tags(date_tag, div_tag)
    length_lookaround = lookaround_tags(length_tag, div_tag)
    href_lookaround = lookaround_tags(href, quote)
    gt_a_lookaround = lookaround_tags(gt, a_tag)


    for html_input in search_snippets:
        thiscourse = {}
        title_outer_text = return_lookaround_text(title_lookaround.search(html_input))
        if title_outer_text:
            url_text = return_lookaround_text(href_lookaround.search(title_outer_text))
            name_text = return_lookaround_text(gt_a_lookaround.search(title_outer_text))
            course_id = url_text.split('/')[-1]
            author_text = return_lookaround_text(author_lookaround.search(html_input))
            level_text = return_lookaround_text(level_lookaround.search(html_input))
            date_text = return_lookaround_text(date_lookaround.search(html_input))
            length_text = return_lookaround_text(length_lookaround.search(html_input))
            lenght = get_length(length_text)
            rating_snippet = outer_search_snippet(html_input, r'search-result__rating')
            rating = return_rating(rating_snippet)
            
            if author_text and not '{' in author_text:
                thiscourse['url'] = url_text.strip()
                thiscourse['title'] = name_text.strip()
                thiscourse['author'] = author_text.strip().split('by ')[-1]
                thiscourse['level'] = level_text.strip()
                thiscourse['date'] = date_text.strip()
                thiscourse['length'] = lenght
                thiscourse['rating'] = rating
                course_dict[course_id] = thiscourse
    
    print('')
    print('Loaded', len(course_dict), 'courses.', 'Saving results to', JSON_OUTPUT_FILE)
    store_dict_as_json(course_dict, JSON_OUTPUT_FILE)
    print('Done.')


if __name__ == "__main__":
    main()