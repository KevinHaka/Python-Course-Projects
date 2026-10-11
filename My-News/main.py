import os.path
import urllib.request
import urllib.error
import re
import datetime
import util
# τα ονόματα βοηθητικών αρχείων
data_dir = os.getcwd() # ο φάκελος για αποθήκευση δεδομένων εφαρμογής
feeds_file = os.path.join(data_dir, 'news.csv') # αρχείο με κατηγορίες από rss feeds
users_file = os.path.join(data_dir, 'users.csv') # αρχείο με προφιλ χρηστών
WIDTH = 70  #πλάτος κειμένου είδησης
URL = "http://rss.in.gr/" # διεύθυνση ειδήσεων
# καθολική μεταβλητή
user = {} # καθολική μεταβλητή που περιέχει τα στοιχεία του συνδεδεμένου κάθε φορά χρήστη
# στη μορφή: user = {'user': 'nikos', 'areas': {'Ειδήσεις Πολιτισμός': ['Καζαντζάκη'], 'Υγεία': []}

def login_user():
    '''
    Ζητάει username από χρήστη και διαχειρίζεται τη σύνδεση.
    Επιστρέφει True αν η σύνδεση ήταν επιτυχής, False αλλιώς.
    '''

    username = input("User login: ").strip()
    if username:
        if username.lower() == 'admin': admin()
        
        else:
            if retrieve_user(username):
                print(f"\nΚαλώς ήρθατε, {username}!\n")
                return True
            
            else:
                create_profile = input(
                    "\nΔεν υπάρχει χρήστης με αυτό το όνομα. Θα θέλατε να δημιουργήσετε προφίλ; (ναι/οχι): "
                ).strip().lower()
                

                if create_profile.lower() in ['ναι', 'nai', 'ν', 'n']:
                    global user
                    user = {'user': username, 'areas': {}}
                    
                    update_user()

                    print(f"\nΚαλώς ήρθατε, {username}!\n")
                    return True

    return False

def admin():
    '''
    Διαχείριση χρηστών (προσθήκη/διαγραφή).
    Προσβάσιμη μόνο από διαχειριστή.
    '''

    print("\nΈχετε δικαιώματα διαχειριστή")
    print("----------------------------")
      
    while True:
        data = util.csv_to_dict('users.csv')
        users = list(set(entry['user'] for entry in data))  

        print("\nΚαταχωρημένοι χρήστες:", users)
        action = input(
            "Διαχείριση χρηστών, +χρήστης (προσθήκη νέου χρήστη), -χρήστης (διαγραφή χρήστη): "
        ).strip()

        if not action: break
        print()

        if action.startswith('+'):
            new_user = action[1:].strip()

            # Έλεγχος για κενό username
            if not new_user:
                print("Δεν δώσατε όνομα χρήστη.")
            
            # Έλεγχος για admin
            elif new_user.lower() == 'admin':
                print("Το 'admin' είναι δεσμευμένο όνομα χρήστη και δεν μπορεί να προστεθεί.")

            elif new_user in users:
                print(f"Ο χρήστης {new_user} υπάρχει ήδη.")

            else:
                data.append({'user': new_user, 'area': '', 'keywords': ''})
                util.dict_to_csv(data, 'users.csv')
                print(f"Ο χρήστης {new_user} προστέθηκε.")
        
        elif action.startswith('-'):
            del_user = action[1:].strip()
            
            if not del_user:
                print("Δεν δώσατε όνομα χρήστη.")

            elif del_user not in users:
                print(f"Ο χρήστης {del_user} δεν υπάρχει.")

            else:
                # Επαλήθευση διαγραφής
                confirm = input(f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον χρήστη '{del_user}'; (y/n): ").strip().lower()

                if confirm in ['yes', 'y', 'ναι', 'ν']:
                    data = [entry for entry in data if entry['user'] != del_user]
                    util.dict_to_csv(data, 'users.csv')
                    print(f"Ο χρήστης {del_user} διαγράφηκε.")
                
                else:
                    print(f"Η διαγραφή του χρήστη {del_user} ακυρώθηκε.")

        else:
            print("Μη έγκυρη εντολή.")
            print("Μάλλον ξεχάσατε το + ή - πριν το όνομα χρήστη.")
            print("Παρακαλώ προσπαθήστε ξανά.")

def retrieve_user(username):
    '''
    Ανακτά τα στοιχεία χρήστη από το αρχείο.
    :param username: το όνομα χρήστη
    :return: True αν βρέθηκε ο χρήστης, False αλλιώς
    '''

    data = util.csv_to_dict('users.csv')
    user_entries = [entry for entry in data if entry['user'] == username]
    
    if user_entries:
        global user
        user = {'user': username, 'areas': {}}

        for entry in user_entries:
            area = entry['area']

            if area:
                raw_keywords = entry['keywords']
                keywords = raw_keywords.split('$') if raw_keywords else []
                user['areas'][area] = keywords

        return True
    return False

def update_user():
    '''
    Αποθηκεύει το προφίλ του τρέχοντος χρήστη στο αρχείο.
    '''

    global user
    data = util.csv_to_dict('users.csv')
    
    not_user_entries = [entry for entry in data if entry['user'] != user['user']]
    user_entries = []

    if user['areas']:
        for area, keywords in user['areas'].items():
            keywords_str = '$'.join(keywords) if keywords else ''
            user_entries.append({'user': user['user'], 'area': area, 'keywords': keywords_str})

    else: 
        user_entries.append({'user': user['user'], 'area': '', 'keywords': ''})

    util.dict_to_csv(not_user_entries + user_entries, 'users.csv')

def load_newsfeeds():
    '''
    Η συνάρτηση φορτώνει τις διευθύνσεις των rss feed urls στο λεξικό feeds από το σχετικό αρχείο
    επιστρέφει το λεξικό που ανακτάται ή επιστρέφει False αν το αρχείο feeds_file δεν υπάρχει
    '''
    if os.path.isfile(feeds_file) :
        return util.csv_to_dict(feeds_file)
    else:
        print('Δεν υπάρχει αρχείο {}'.format(feeds_file))
        return False

def load_news_to_temp(feeds):
    '''
    Άνοιγμα του rss feed,
    :param feeds οι θεματικές περιοχές ειδήσεων με τις αντίστοιχες διευθύνσεις των rss feeds
    φορτώνει τα άρθρα και τα αποθηκεύει σε προσωρινό αρχείο
    '''
    count = 0
    news_items = []
    for area in user['areas']:
        print(area, ' ....', end='')
        url = [x['rss'] for x in feeds if x['title'] == area]
        if url:
            url = url[0]
            req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as response:
                html = response.read().decode()
            filename = "tempfile.rss"
            with open(filename, "w", encoding="utf-8") as p:
                p.write(html)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.readline())
        except urllib.error.URLError as e:
            print(e)
            if hasattr(e, 'reason'):  # χωρίς σύνδεση ιντερνετ
                print('Αποτυχία σύνδεσης στον server')
                print('Αιτία: ', e.reason)
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                rss = f.read().replace("\n", " ")
                items = re.findall(r"<item>(.*?)</item>", rss, re.MULTILINE | re.IGNORECASE)
                count_area_items = 0
                for item in items:
                    news_item = {}
                    title = re.findall(r"<title>(.*?)</title>", item, re.MULTILINE | re.IGNORECASE)
                    date = re.findall(r"<pubdate>(.*?)</pubdate>", item, re.MULTILINE | re.IGNORECASE)
                    if len(title) > 0:
                        title = title[0]
                    else: title = ''
                    date = format_date(date[0]) if date else ' '
                    content = re.findall(r"<description>(.*?)</description>", item, re.MULTILINE | re.IGNORECASE)
                    found = False
                    if user['areas'][area]:
                        for k in user['areas'][area]:
                            if check_keyword(k, title) or check_keyword(k, content[0]):
                                found = True
                                break
                    else: found = True
                    if found:
                        count += 1
                        count_area_items += 1
                        news_item = {'no':count, 'title': title, 'date':date, 'content': content[0]}
                        news_items.append(news_item)
                        if count> 99: break # μόνο 100 πρώτες ειδήσεις
                print(count_area_items, end= ' ,   ')
    util.dict_to_csv(news_items, 'mytemp.csv') # temporary store of news items
    print()
    return len(news_items)

def print_titles():
    '''
    Η συνάρτηση αυτή τυπώνει τους τίτλους των ειδήσεων που υπάρχουν στο αρχείο mytemp.csv
    :return:
    '''
    try:
        news_items = util.csv_to_dict('mytemp.csv')
        for item in news_items:
            print(item['no'] + ' [' + item['date'] + ']\t' + item['title'])
        return True
    except FileNotFoundError:
        return False

def print_news_item(item_no):
    '''
    Τυπώνει την είδηση με τον συγκεκριμένο αριθμό.
    :param item_no: ο αριθμός της είδησης
    :return: True αν η είδηση βρέθηκε, False αλλιώς
    '''
    
    data = util.csv_to_dict('mytemp.csv')
    
    for entry in data:
        no = entry['no']

        if int(no) == item_no:
            pattern = r"</div>(.*)\]\]>$"

            title = entry['title']
            date = entry['date']
            content = entry['content']
            content = re.findall(pattern, content)[0].strip()

            formatted_print(f"\n{no} [{date}] {title}\n")
            formatted_print(content)

            return True
    return False

def format_date(date):
    # βοηθητική συνάρτηση για διαμόρφωση της ημερομηνίας της είδησης
    m_gr = 'Ιαν Φεβ Μαρ Απρ Μαϊ Ιουν Ιουλ Αυγ Σεπ Οκτ Νοε ∆εκ'.split()
    m_en = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
    d = re.findall(r"([0-9]{2}\s[A-Z][a-z]{2}\s[0-9]{4})",date, re.I)
    if d : date = d[0].split()
    #if d: date = d.group(0).split()
    if date[1] in m_en: date[1] = m_gr[m_en.index(date[1])]
    return ' '.join(date)

def check_keyword(keyword, text):
    # βοηθητική συνάρτηση που αναζητάει το keyword σε μια συμβολοσειρά text. Επιστρέφει True/False αν βρεθεί ή όχι.
    tonoi = ('αά', 'εέ', 'ηή', 'ιί', 'οό', 'ύυ', 'ωώ')
    n_phrase= ''
    for c in keyword:
        char = c
        for t in tonoi:
            if c in t: char = '['+t+']'
        n_phrase += char
    pattern = r'.*'+n_phrase+r'.*'
    w =re.findall(pattern, text, re.I)
    if w:
        return True
    else:
        return False

def formatted_print(st, width=WIDTH):
    # συνάρτηση που τυπώνει συμβολοσειρά st με πλάτος width χαρακτήρων
    para = st.split("\n")
    for p in para:
        st = p.split()
        out = ""
        while True:
            while len(st) > 0 and len(out+st[0]) < width :
                out = " ".join([out, st.pop(0)])
            print(out)
            out = ""
            if len(st) == 0 : break

def manage_profile(feeds):
    '''
    Διαχείριση προφίλ χρήστη (θέματα ειδήσεων και όροι αναζήτησης).
    :param feeds: λίστα διαθέσιμων θεμάτων ειδήσεων
    '''
    global user
    modify = False
    while True:
        print_user_profile()
        print(WIDTH * '_')
        reply = input('Θέλετε να αλλάξετε το προφίλ σας; (Ναι για αλλαγές)')
        if not reply or reply[0].lower() not in 'νn': break
        print('Αρχικά θα μπορείτε να επιλέξετε από θέματα ειδήσεων, στη συνέχεια να ορίσετε όρους αναζήτησης σε καθένα από αυτά')
        main_feeds = [x['title'] for x in feeds ]
        
        # Επιλογή θεμάτων ειδήσεων
        while True:
            print('\nΤα διαθέσιμα θέματα ειδήσεων είναι:')
            for i, area in enumerate(main_feeds):
                print(f"\t{i:2d} - {area}")
            
            user_areas_str = ", ".join([area for area in user['areas'].keys()])
            user_areas_str = user_areas_str if user_areas_str else "ΔΕΝ ΥΠΑΡΧΟΥΝ ΘΕΜΑΤΑ"
            print(f"\nΤα θέματα ενδιαφέροντός σας είναι: {user_areas_str}")

            reply = input("Μπορείτε να προσθέσετε θέματα με +αριθμός ή να αφαιρέσετε θέματα ειδήσεων με -αριθμός. Πατήστε Enter για συνέχεια... ")
            if not reply: break
            print()
            add_remove = reply.split(' ')

            for ar in add_remove:
                if ar.startswith('+'):
                    try:
                        index = int(ar[1:])

                        if 0 <= index < len(main_feeds):
                            area_to_add = main_feeds[index]

                            if area_to_add not in user['areas']:
                                user['areas'][area_to_add] = []
                                modify = True

                        else: print(f"Μη έγκυρος αριθμός: {index}")
                    except ValueError: print(f"Μη έγκυρη εντολή: {ar}")

                elif ar.startswith('-'):
                    try:
                        index = int(ar[1:])

                        if 0 <= index < len(main_feeds):
                            area_to_remove = main_feeds[index]

                            if area_to_remove in user['areas']:
                                del user['areas'][area_to_remove]
                                modify = True

                        else: print(f"Μη έγκυρος αριθμός: {index}")
                    except ValueError: print(f"Μη έγκυρη εντολή: {ar}")
                else: print(f"Μη έγκυρη εντολή: {ar}, πρέπει να ξεκινάει με + ή -")

        print_user_profile()
        print('\nΤώρα για κάθε θέμα ειδήσεων μπορείτε να επιλέξετε όρους αναζήτησης')
        
        # Επιλογή όρων αναζήτησης για κάθε θέμα
        for area in user['areas'].keys():
            while True:
                print(f"\nΘΕΜΑ ειδήσεων: {area}")
                print(f"Οι τρέχοντες όροι αναζήτησης είναι: [{', '.join(user['areas'][area])}]")
                reply = input("Προσθέστε όρους με +λέξη ή αφαιρέστε όρους με -λέξη. Πατήστε Enter για συνέχεια... ")

                if not reply: break
                print()
                add_remove = reply.split(' ')

                for ar in add_remove:
                    if ar.startswith('+'):
                        keyword_to_add = ar[1:]

                        if keyword_to_add and keyword_to_add not in user['areas'][area]:
                            user['areas'][area].append(keyword_to_add)
                            modify = True

                    elif ar.startswith('-'):
                        keyword_to_remove = ar[1:]

                        if keyword_to_remove in user['areas'][area]:
                            user['areas'][area].remove(keyword_to_remove)
                            modify = True

                    else: print(f"Μη έγκυρη εντολή: {ar}, πρέπει να ξεκινάει με + ή -")

        print_user_profile()
        reply = input('\n ... Θέλετε άλλες αλλαγές στο προφίλ σας (ναι για αλλαγές))')
        if not reply or reply[0].lower() != 'ν': break
    if modify:
        update_user()

def print_user_areas(li):
    '''
    Τυπώνει τα θέματα ειδήσεων που ενδιαφέρουν τον χρήστη από τη λίστα li.
    '''
    print('\nΤα ενδιαφέροντά σας είναι ...', end='')
    items = False
    for item in li:
        if item in user['areas'].keys():
            print(item, end=', ')
            items = True
    if not items: print('ΚΑΝΕΝΑ ΕΝΔΙΑΦΕΡΟΝ', end='')
    print()

def print_user_profile():
    '''
    Τυπώνει το πλήρες προφίλ του χρήστη (θέματα και όρους αναζήτησης).
    '''
    print('\nΤα θέματα ειδήσεων που σας ενδιαφέρουν είναι:')
    if not user['areas']: print('KENO ΠΡΟΦΙΛ ΧΡΗΣΤΗ')
    for area in user['areas']:
        print(area)
        for keyword in user['areas'][area]:
            print('\t\t', keyword)

def clear_temps():
    '''
    Διαγράφει τα προσωρινά αρχεία που δημιουργήθηκαν.
    '''

    files = os.listdir(os.getcwd())
    temp_files = [os.path.join(data_dir, f) for f in files if 'temp' in f]

    for temp_file in temp_files:
        if os.path.isfile(temp_file):
            os.remove(temp_file)

def main():
    '''
    Κύριο πρόγραμμα: διαχείριση σύνδεσης χρήστη και μενού επιλογών.
    '''
    print("Σήμερα είναι :", str(datetime.datetime.today()).split()[0])
    username = login_user()
    if username:
        feeds = load_newsfeeds()
        if feeds:
            print('To mynews πρoσφέρει προσωποποιημένες ειδήσεις από το in.gr')
            while True: # main menu
                print(WIDTH * '=')
                user_selected = input('(Π)ροφίλ ενδιαφέροντα, (Τ)ίτλοι ειδήσεων, (enter)Εξοδος\n')
                if user_selected == '': # έξοδος
                    break
                elif user_selected.upper() in 'ΠP': # προφίλ
                    manage_profile(feeds) # διαχείριση του προφίλ χρήστη
                elif user_selected.upper() in 'ΤT': # παρουσίαση τίτλων ειδήσεων
                    if 'areas' in user.keys() and len(user['areas']) > 0 : # αν ο χρήστης έχει ορίσει areas
                        print_user_profile()
                        print('\nΤΕΛΕΥΤΑΙΕΣ ΕΙΔΗΣΕΙΣ ΠΟΥ ΣΑΣ ΕΝΔΙΑΦΕΡΟΥΝ...ΣΕ ΤΙΤΛΟΥΣ')
                        items_count = load_news_to_temp(feeds)  # φόρτωσε τις ειδήσεις που ενδιαφέρουν τον χρήστη
                        if items_count: # εαν υπάρχουν ειδήσεις σύμφωνα με το προφιλ του χρήστη ...
                            print_titles() # τύπωσε τους τίτλους των ειδήσεων του χρήστη
                            while True:
                                print(WIDTH * '_')
                                item_no = input('Επιλογή είδησης (1 .. {}) ή <enter> για να συνεχίσετε:'.format(items_count))
                                if item_no == '': break
                                if item_no.isdigit() and 0 < int(item_no) <= items_count:
                                    print_news_item(int(item_no))
                        else: print('Δεν υπάρχουν ειδήσεις με βάση το προφίλ ενδιαφερόντων σας ...')
                    else: print('Πρέπει πρώτα να δημιουργήσετε το προφίλ σας')
    clear_temps()
    print('\nΕυχαριστούμε')


if __name__ == '__main__': main()