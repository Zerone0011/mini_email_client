import json
import os
from datetime import datetime

USERS_FILE = 'users.json'
INBOX_FILE = 'inboxes.json'


def load_json(filename: str) -> dict:
    """
    Loads JSON data from a file.

    Args:
        filename (str): The path to the JSON file.

    Returns:
        dict: The data loaded from the JSON file. Returns an empty dictionary if the file does not exist.
    """
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}


def save_json(filename: str, data: dict) -> None:
    """
    Saves data to a file in JSON format.

    Args:
        filename (str): The path to the JSON file.
        data (dict): The data to save.

    Returns:
        None
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


# -------------------- User Functions -------------------- #
def register_user(users: dict[str, str]) -> None:
    """
    Registers a new user by prompting for a username and password.

    Args:
        users (dict[str, str]): A dictionary of existing users with usernames as keys and passwords as values.

    Returns:
        None
    """
    print("\n" + "=" * 60)
    print("USER REGISTRATION".center(60))
    print("=" * 60)
    while True:
        username = input("Choose a username: ").strip()
        if username in users:
            print("Username already exists. Try a different one.")
        else:
            break
    password = input("Choose a password: ").strip()
    users[username] = password
    save_json(USERS_FILE, users)
    print(f"User '{username}' registered successfully!\n")


def login(users: dict[str, str]) -> str | None:
    """
    Handles user login by verifying the username and password.

    Args:
        users (dict[str, str]): A dictionary of existing users with usernames as keys and passwords as values.

    Returns:
        str | None: The username of the logged-in user if successful, otherwise None.
    """
    print("\n" + "=" * 60)
    print("LOGIN".center(60))
    print("=" * 60)
    MAX_TRIES = 3
    tries = 0
    while tries < MAX_TRIES:
        username = input("Enter your username: ").strip()
        if username not in users:
            print("User does not exist. Try again.")
            tries += 1
            continue
        password = input("Enter your password: ").strip()
        if users[username] == password:
            print(f"Login successful. Welcome, {username}!")
            return username
        else:
            print("Incorrect password. Try again.")
            tries += 1
    print("Maximum login attempts reached. Returning to the main menu.")
    return None


def change_password(username: str, users: dict[str, str]) -> None:
    """
    Allows a user to change their password.

    Args:
        username (str): The username of the user changing their password.
        users (dict[str, str]): A dictionary of existing users with usernames as keys and passwords as values.

    Returns:
        None
    """
    print("\n" + "=" * 60)
    print("CHANGE PASSWORD".center(60))
    print("=" * 60)
    old_password = input("Enter your current password: ").strip()
    if users.get(username) != old_password:
        print("Incorrect password.")
        return
    new_password = input("Enter your new password: ").strip()
    users[username] = new_password
    save_json(USERS_FILE, users)
    print("Password updated successfully.")


# -------------------- Mailbox Structure -------------------- #
def ensure_user_box(username: str, inboxes: dict[str, dict[str, list]]) -> None:
    """
    Ensures that the given username has an entry in the inboxes dictionary.

    If the username does not exist in the inboxes, it initializes the user's
    mailbox structure with empty lists for 'inbox', 'drafts', and 'sent'.

    Args:
        username (str): The username to check or add to the inboxes.
        inboxes (dict[str, dict[str, list]]): The dictionary containing all user mailboxes.

    Returns:
        None
    """
    if username not in inboxes:
        inboxes[username] = {"inbox": [], "drafts": [], "sent": []}


# -------------------- Mail Function -------------------- #
def compose_email(sender: str) -> tuple[dict, list[str], str]:
    """
    Composes an email by prompting the user for recipients, subject, and body.

    Args:
        sender (str): The username of the sender.

    Returns:
        tuple[dict, list[str], str]: A tuple containing:
            - The email as a dictionary with keys 'from', 'to', 'subject', 'body', 'time', and 'read'.
            - A list of recipient usernames.
            - A string indicating the action ('send' or 'draft').
    """
    print("\n" + "=" * 60)
    print("COMPOSE EMAIL".center(60))
    print("=" * 60)
    recipients = input("Recipients (comma separated): ").strip().split(",")
    recipients = [r.strip() for r in recipients if r.strip()]
    subject = input("Subject: ").strip()
    body = input("Message:\n").strip()
    time = datetime.now().isoformat(timespec='seconds')
    email = {
        'from': sender,
        'to': recipients,
        'subject': subject,
        'body': body,
        'time': time,
        'read': False
    }
    action = input("Send now or save as draft? (send/draft): ").strip().lower()
    return email, recipients, action


def send_email(sender: str, inboxes: dict[str, dict[str, list]]) -> None:
    """
    Handles the process of composing and sending an email or saving it as a draft.

    Args:
        sender (str): The username of the sender.
        inboxes (dict[str, dict[str, list]]): The dictionary containing all user mailboxes.

    Returns:
        None
    """
    email, recipients, action = compose_email(sender)
    ensure_user_box(sender, inboxes)
    if action == 'send':
        for recipient in recipients:
            ensure_user_box(recipient, inboxes)
            inboxes[recipient]["inbox"].append(email.copy())
        inboxes[sender]["sent"].append(email)
        print(f"\nEmail sent to: {', '.join(recipients)}")
    elif action == 'draft':
        inboxes[sender]["drafts"].append(email)
        print("Email saved to drafts.")
    else:
        print("Invalid option. Email not sent.")


def view_inbox(username: str, inboxes: dict[str, dict[str, list[dict]]]) -> None:
    """
    Displays the inbox of the specified user.

    This function ensures the user's mailbox exists, retrieves the inbox,
    and displays all emails sorted by time in ascending order. Marks emails
    as read after displaying them.

    Args:
        username (str): The username of the user whose inbox is to be viewed.
        inboxes (dict[str, dict[str, list[dict]]]): The dictionary containing all user mailboxes.

    Returns:
        None
    """
    ensure_user_box(username, inboxes)
    inbox = inboxes[username]["inbox"]
    if not inbox:
        print("\nYour inbox is empty.")
        return
    print("\n" + "=" * 60)
    print(f"{username.upper()}'S INBOX".center(60))
    print("=" * 60)
    sorted_inbox = sorted(inbox, key=lambda m: m['time'], reverse=False)
    for idx, msg in enumerate(sorted_inbox):
        status = "[NEW] " if not msg.get("read", False) else ""
        print(f"\n[{idx}] {status}From: {msg['from']} | Time: {msg['time']}")
        print(f"Subject: {msg['subject']}")
        print(f"Message:\n{msg['body']}")
        msg['read'] = True
        print("-" * 60)


def view_sent(username: str, inboxes: dict[str, dict[str, list[dict]]]) -> None:
    """
    Displays the sent emails of the specified user.

    This function ensures the user's mailbox exists, retrieves the sent emails,
    and displays all emails sorted by time in descending order.

    Args:
        username (str): The username of the user whose sent emails are to be viewed.
        inboxes (dict[str, dict[str, list[dict]]]): The dictionary containing all user mailboxes.

    Returns:
        None
    """
    ensure_user_box(username, inboxes)
    sent = inboxes[username]["sent"]
    if not sent:
        print("\nNo sent messages.")
        return
    print("\n" + "=" * 60)
    print(f"{username.upper()}'S SENT MAILS".center(60))
    print("=" * 60)
    sorted_sent = sorted(sent, key=lambda m: m['time'], reverse=True)
    for idx, msg in enumerate(sorted_sent):
        print(f"\n[{idx}] To: {', '.join(msg['to'])} | Time: {msg['time']}")
        print(f"Subject: {msg['subject']}")
        print(f"Message:\n{msg['body']}")
        print("-" * 60)


def view_drafts(username: str, inboxes: dict[str, dict[str, list[dict]]]) -> None:
    """
    Displays the drafts of the specified user and allows sending or deleting drafts.

    This function ensures the user's mailbox exists, retrieves the drafts,
    and displays all drafts. The user can choose to send or delete a draft.

    Args:
        username (str): The username of the user whose drafts are to be viewed.
        inboxes (dict[str, dict[str, list[dict]]]): The dictionary containing all user mailboxes.

    Returns:
        None
    """
    ensure_user_box(username, inboxes)
    drafts = inboxes[username]["drafts"]
    if not drafts:
        print("\nNo drafts saved.")
        return
    print("\n" + "=" * 60)
    print(f"{username.upper()}'S DRAFTS".center(60))
    print("=" * 60)
    for idx, msg in enumerate(drafts):
        print(f"\n[{idx}] To: {', '.join(msg.get('to', []))} | Time: {msg['time']}")
        print(f"Subject: {msg['subject']}")
        print(f"Message:\n{msg['body']}")
        print("-" * 60)

    choice = input("Send or delete a draft? (send <index> / del <index> / cancel): ").strip()
    if choice.startswith("send"):
        try:
            index = int(choice.split()[1])
            draft = drafts.pop(index)
            for recipient in draft.get("to", []):
                ensure_user_box(recipient, inboxes)
                inboxes[recipient]["inbox"].append(draft.copy())
            inboxes[username]["sent"].append(draft)
            print("Draft sent successfully!")
        except Exception:
            print("Invalid index.")
    elif choice.startswith("del"):
        try:
            index = int(choice.split()[1])
            drafts.pop(index)
            print("Draft deleted.")
        except Exception:
            print("Invalid index.")
    else:
        print("Cancelled.")


def delete_email(username: str, inboxes: dict[str, dict[str, list[dict]]]) -> None:
    """
    Deletes an email from the user's inbox.

    This function displays the user's inbox, prompts the user to select an email
    by its index, and deletes the selected email if the index is valid.

    Args:
        username (str): The username of the user whose email is to be deleted.
        inboxes (dict[str, dict[str, list[dict]]]): The dictionary containing all user mailboxes.

    Returns:
        None
    """
    ensure_user_box(username, inboxes)
    inbox = inboxes[username]["inbox"]
    if not inbox:
        print("\nNo emails to delete.")
        return
    view_inbox(username, inboxes)
    try:
        index = int(input("Enter the index of the message to delete: "))
        if 0 <= index < len(inbox):
            deleted = inbox.pop(index)
            print(f"Deleted message from {deleted['from']}")
        else:
            print("Invalid index.")
    except ValueError:
        print("Please enter a valid number.")


def search_emails(username: str, inboxes: dict[str, dict[str, list[dict]]]) -> None:
    """
    Searches for emails in the user's inbox that match a given keyword in the subject or body.

    This function ensures the user's mailbox exists, prompts the user for a keyword,
    and displays all matching emails. If no matches are found, it notifies the user.

    Args:
        username (str): The username of the user whose inbox is to be searched.
        inboxes (dict[str, dict[str, list[dict]]]): The dictionary containing all user mailboxes.

    Returns:
        None
    """
    ensure_user_box(username, inboxes)
    keyword = input("\nKeyword to search in subject/body: ").strip().lower()
    results = []
    for idx, msg in enumerate(inboxes[username]["inbox"]):
        if keyword in msg['subject'].lower() or keyword in msg['body'].lower():
            results.append((idx, msg))
    if not results:
        print("No matching emails found.")
    else:
        print("\n" + "=" * 60)
        print("SEARCH RESULTS".center(60))
        print("=" * 60)
        for idx, msg in results:
            print(f"\n[{idx}] From: {msg['from']} | Time: {msg['time']}")
            print(f"Subject: {msg['subject']}")
            print(f"Message:\n{msg['body']}")
            print("-" * 60)


# -------------------- menu -------------------- #
def main_menu(current_user: str, users: dict[str, str], inboxes: dict[str, dict[str, list[dict]]]) -> None:
    """
    Displays the main menu for the logged-in user and handles user actions.

    This function provides options for the user to view their inbox, compose emails,
    manage drafts, view sent emails, delete emails, search emails, change their password,
    switch users, or exit the application.

    Args:
        current_user (str): The username of the currently logged-in user.
        users (dict[str, str]): A dictionary of all registered users with their passwords.
        inboxes (dict[str, dict[str, list[dict]]]): A dictionary containing all user mailboxes.

    Returns:
        None
    """
    while True:
        print("\n" + "=" * 60)
        print(f"Welcome, {current_user}!".center(60))
        print("=" * 60)
        print("1. View Inbox")
        print("2. Compose Email")
        print("3. View Drafts")
        print("4. View Sent Mails")
        print("5. Delete Email")
        print("6. Search Emails")
        print("7. Change Password")
        print("8. Switch User")
        print("9. Exit")
        print("-" * 60)

        choice = input("Enter choice (1-9): ").strip()
        if choice == '1':
            view_inbox(current_user, inboxes)
        elif choice == '2':
            send_email(current_user, inboxes)
        elif choice == '3':
            view_drafts(current_user, inboxes)
        elif choice == '4':
            view_sent(current_user, inboxes)
        elif choice == '5':
            delete_email(current_user, inboxes)
        elif choice == '6':
            search_emails(current_user, inboxes)
        elif choice == '7':
            change_password(current_user, users)
        elif choice == '8':
            return
        elif choice == '9':
            save_json(INBOX_FILE, inboxes)
            save_json(USERS_FILE, users)
            print("\nAll data saved. Goodbye!")
            exit()
        else:
            print("Invalid choice. Try again.")


# -------------------- Program entry -------------------- #
def main():
    print("=" * 60)
    print("WELCOME TO MINIMAIL+".center(60))
    print("=" * 60)
    users = load_json(USERS_FILE)
    inboxes = load_json(INBOX_FILE)

    while True:
        print("\nMain Menu")
        print("1. Login")
        print("2. Register New User")
        print("3. Exit")
        print("-" * 60)
        action = input("Enter choice (1-3): ").strip()

        if action == '1':
            current_user = login(users)
            if current_user is None:
                continue
            ensure_user_box(current_user, inboxes)
            main_menu(current_user, users, inboxes)
        elif action == '2':
            register_user(users)
        elif action == '3':
            save_json(INBOX_FILE, inboxes)
            save_json(USERS_FILE, users)
            print("All data saved. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
