from helpers import auto_log, get_by_id, align_input, query_db, check_loans
from books import Book
from config import RE_PATT_D, ERRORS


def book_menu():
    """
       Displays the book menu and handles user interaction for book-related actions.

       Offers options to add, edit, delete, display all books, or return to the main menu.
       Validates user input and calls the appropriate functions based on the selected action.
       """

    # Displaying book-related action choices to the user
    book_actions = ['1', '2', '3', '4', '0']
    print("\n[1] Add a book\n"
          "[2] Edit a book\n"
          "[3] Delete a book\n"
          "[4] Display all books\n"
          "[0] Return to the Main Menu")
    book_act = input("-->")

    # Validating user input to ensure it matches one of the available actions
    while book_act not in book_actions:
        print("Invalid entry. Please choose one of the options in the menu")
        book_act = input('-->')

    # Matching the user's choice with the corresponding function
    match book_act:
        case '1':
            add_book()
            book_menu()
        case '2':
            id_input = align_input('ID number: ', RE_PATT_D['bookID'], ERRORS['bookID'])
            edit_book(get_book(id_input))
            book_menu()
        case '3':
            id_input = align_input('ID number: ', RE_PATT_D['bookID'], ERRORS['bookID'])
            delete_book(get_book(id_input))
            book_menu()
        case '4':
            display_all_books()
            book_menu()
        case '0':
            return # Returning to the main menu


def get_book_d():
    """
      Gathers input from the user for new book details.

      Prompts for book title, author's first and last name, publication year, and book type.
      Validates the input using regular expressions and custom error messages.
      Returns a dictionary of the inputted book details or '0' to exit.

      Returns:
          dict or str: Dictionary of book details or '0' for exit.
      """

    # Prompting user for new book details
    print("Please enter new book details:")

    # Getting and validating book information
    book_title_input = align_input('Book title:', RE_PATT_D['title'], ERRORS['title']).title()
    if book_title_input == '0':
        return '0'
    author_pname_input = align_input("Author's first name:", RE_PATT_D['p_name'], ERRORS['p_name']).title()
    if author_pname_input == '0':
        return '0'
    author_lname_input = align_input("Author's last name: ", RE_PATT_D['l_name'], ERRORS['l_name']).title()
    if author_lname_input == '0':
        return '0'
    pub_year_input = align_input('Publication year:', RE_PATT_D['pub_year'], ERRORS['pub_year'], number='year')
    if pub_year_input == '0':
        return '0'
    book_type_input = align_input('Book type: ', RE_PATT_D['book_type'], ERRORS['book_type'])
    if book_type_input == '0':
        return '0'

    # Returning a dictionary with the collected book details
    return {'title': book_title_input, 'auth_pname': author_pname_input, 'auth_lname': author_lname_input,
            'pub_year': pub_year_input, 'book_type': book_type_input}


def get_book(id_num):
    """
       Retrieves a book object by its ID.

       Args:
           id_num (int): The ID number of the book to retrieve.

       Handles exceptions and validates the input ID.
       Displays book details if found, otherwise prompts for re-entry.

       Returns:
           Book: The book object corresponding to the given ID.
       """

    book_data = None

    # Looping until valid book data is retrieved using the provided ID
    while not book_data:
        try:
            book_data = get_by_id(id_num, table='books') # Attempting to retrieve book data by ID
        except Exception as e:
            print(e) # Printing any exceptions encountered
            id_num = align_input('Enter book ID: ', RE_PATT_D['bookID'], ERRORS['bookID']) # Re-prompting for book ID

    # Attempting to create a Book object with the retrieved data
    try:
        book = Book(title=book_data[1], author_pname=book_data[2], author_lname=book_data[3],
                    year_published=book_data[4],
                    book_type=book_data[5], id_=book_data[0], override_id=True)
    except Exception as e:
        print(e)  # Handling any exceptions during Book object creation
        book_menu()  # Returning to the book menu if an exception occurs
        return

    book.show()  # Displaying the book details

    return book  # Returning the Book object


def add_book():
    """
       Handles the process of adding a new book to the library.

       Gathers book details from the user, creates a Book object, and saves it to the database.
       Logs the action and displays a success message upon completion.
       """
    # Book addition process with exception handling and success message
    book_d = get_book_d()  # Getting book details from the user
    if book_d == '0':
        return  # Exiting the function if user inputs '0'

    # Attempting to create and save a new Book object
    try:
        b = Book(title=book_d['title'], author_pname=book_d['auth_pname'], author_lname=book_d['auth_lname'],
                 year_published=book_d['pub_year'], book_type=book_d['book_type'])
    except Exception as e:
        print(e)  # Handling exceptions during Book object creation
        add_book()  # Re-prompting for book details in case of an exception
        return

    b.save()  # Saving the new book to the database

    auto_log('Book added', log_id=b.id)  # Logging the book addition
    print("\n*** Book added successfully! ***\n")  # Displaying a success message


def edit_book(book):
    """
       Provides options to edit different attributes of a given book.

       Args:
           book (Book): The book object to be edited.

       Allows editing of the book's title, author's name, publication year, and type.
       Validates the user's choices and updates the book details accordingly.
       """
    # Possible actions a user can take within the edit book menu
    possible_actions = ['1', '2', '3', '4', '5', '0']
    values = []  # List to store new values for book attributes
    clauses_lst = []  # List to store SQL clauses for updating book attributes

    while True:
        # Displaying the edit menu options to the user
        print("\n[1] Edit book title\n"
              "[2] Edit book author's first name\n"
              "[3] Edit book author's last name\n"
              "[4] Edit publication year\n"
              "[5] Edit book type\n"
              "[0] Return to Book Menu")
        edit_book_act = input("-->")

        # Validating user input to match available edit actions
        while edit_book_act not in possible_actions:
            edit_book_act = input("-->")

        # Handling user's choice for editing specific book attributes
        match edit_book_act:
            case '1':
                # Loop for editing the book title
                while True:
                    title_input = align_input('Book title:', RE_PATT_D['title'], ERRORS['title']).title()
                    if title_input == '0':
                        return  # Allowing user to exit the process
                    try:
                        book.title = title_input  # Setting new book title
                    except Exception as e:
                        print(e)  # Handling exceptions
                        continue
                    else:
                        clauses_lst.append("title = ?")  # SQL clause for updating title
                        values.append(book._title)  # Adding new value to the values list
                        break

            # Similar structures follow for editing author's first name, last name, publication year, and book type
            case '2':
                while True:
                    auth_pname_input = align_input("Author's first name:", RE_PATT_D['p_name'],
                                                   ERRORS['p_name']).title()
                    if auth_pname_input == '0':
                        return
                    try:
                        book.auth_pname = auth_pname_input
                    except Exception as e:
                        print(e)
                        continue
                    else:
                        clauses_lst.append("author_pname = ?")
                        values.append(book._auth_pname)
                        break
            case '3':
                while True:
                    auth_lname_input = align_input("Author's last name: ", RE_PATT_D['l_name'],
                                                   ERRORS['l_name']).title()
                    if auth_lname_input == '0':
                        return
                    try:
                        book.auth_lname = auth_lname_input
                    except Exception as e:
                        print(e)
                        continue
                    else:
                        clauses_lst.append("author_lname = ?")
                        values.append(book._auth_lname)
                        break
            case '4':
                while True:
                    pub_year_input = align_input('Publication year:', RE_PATT_D['pub_year'],
                                                 ERRORS['pub_year'])
                    if pub_year_input == '0':
                        return
                    try:
                        book.published = pub_year_input
                    except Exception as e:
                        print(e)
                        continue
                    else:
                        clauses_lst.append("publication_year = ?")
                        values.append(book._published)
                        break
            case '5':
                while True:
                    book_type_input = align_input('Book type: ', RE_PATT_D['book_type'], ERRORS['book_type'])
                    if book_type_input == '0':
                        return
                    try:
                        book.book_type = book_type_input
                    except Exception as e:
                        print(e)
                        continue
                    else:
                        clauses_lst.append("type = ?")
                        values.append(book._book_type)
                        break
            case '0':
                return  # Returning to the book menu

                # Prompting user if they want to make additional edits
        print("Anything else to edit?\n"
              "[1] Yes\n"
              "[2] No")
        edit_act = input("-->")
        match edit_act:
            case '1':
                pass  # Continuing the loop if there are more edits to be made
            case '2':
                # Finalizing edits and updating the book in the database
                book.edit(set_clauses=clauses_lst, values=values)
                break

            # Logging the edit action and displaying a success message
        auto_log('Book edited', log_id=book.id)
        print("\n*** Book edited successfully! ***\n")


def delete_book(book):
    """
       Handles the deletion of a book from the library.

       Args:
           book (Book): The book object to be deleted.

       Asks for user confirmation before deletion.
       Checks if the book is currently on loan and prevents deletion if so.
       Logs the action and displays a success message upon completion.
       """
    # Asking for user confirmation before deleting the book
    print("\nConfirm delete?\n"
          "[1] Yes\n"
          "[2] No")
    while True:
        del_book_act = input("-->")
        if del_book_act in ['1', '2']:
            break  # Ensuring valid input for confirmation

    # Handling the user's choice for deletion
    match del_book_act:
        case '1':
            # Checking if the book is currently on loan
            try:
                check_loans(book)
            except AssertionError as e:
                print(e)  # Displaying an error if the book is on loan
                book_menu()  # Returning to the book menu
                return

            auto_log('Book deleted', log_id=book.id)  # Logging the book deletion
            print("\n*** Book deleted successfully ***\n")  # Displaying a success message
            return

        case '2':
            book_menu()  # Returning to the book menu if deletion is not confirmed


def display_all_books():
    """
       Retrieves and displays details of all books in the library.

       Fetches books from the database and prints their details.
       """
    books = Book.load_from_db()  # Retrieving all books from the database

    for b in books:
        b.show()  # Displaying details of each book


def find_book_by_title():
    """
      Searches for books based on a title keyword.

      Allows the user to input a search keyword.
      Queries the database for books with titles matching the keyword.
      Displays the search results.
      """
    # Looping to allow the user to search for books by title
    while True:
        print('\n')
        keyword = f"%{input('Enter search keyword: ')}%"
        if keyword == '%0%':
            return  # Allowing the user to exit the search

        # Querying the database for books matching the search keyword
        query = "SELECT * FROM books WHERE title LIKE ?;"
        res_lst = query_db(query=query, parameters=(keyword,), result=True)

        # Displaying search results or a message if no matches are found
        if len(res_lst) == 0:
            print("\n*** No matching results found ***")
        else:
            print(f"************************************"
                  f"\nFOUND {len(res_lst)} RESULT(S): ")
            for book in res_lst:
                b = Book(title=book[1], author_pname=book[2], author_lname=book[3], year_published=book[4],
                         book_type=book[5], id_=book[0], override_id=True)
                b.show()
            print("*************************************")