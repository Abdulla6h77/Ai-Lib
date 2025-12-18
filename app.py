import streamlit as st
from datetime import date
from db import (
    init_db,
    add_book,
    update_book,
    delete_book,
    get_books,
    get_book_by_id,
    get_available_copies,
    add_member,
    update_member,
    delete_member,
    get_members,
    get_member_by_id,
    borrow_book,
    return_book,
    get_loans,
    get_overdue,
)

st.set_page_config(page_title="Library Management", page_icon="📚", layout="wide")
init_db()

def format_book_option(b):
    return f'{b["title"]} — {b["author"]} (ISBN {b["isbn"]})'

def format_member_option(m):
    return f'{m["name"]} — {m["email"]}'

st.title("Library Management")
section = st.sidebar.radio("Navigate", ["Dashboard", "Books", "Members", "Loans"], index=0)

if section == "Dashboard":
    col1, col2, col3 = st.columns(3)
    books = get_books()
    members = get_members()
    active_loans = get_loans(active_only=True)
    overdue = get_overdue()
    with col1:
        st.metric("Books", len(books))
        st.metric("Members", len(members))
    with col2:
        st.metric("Active Loans", len(active_loans))
    with col3:
        st.metric("Overdue Loans", len(overdue))
    st.subheader("Recent Loans")
    if active_loans:
        st.table(active_loans[:10])
    else:
        st.info("No active loans")

elif section == "Books":
    st.header("Add Book")
    with st.form("add_book"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        isbn = st.text_input("ISBN")
        copies = st.number_input("Total copies", min_value=0, step=1, value=1)
        submitted = st.form_submit_button("Add")
        if submitted:
            if title and author and isbn and copies >= 0:
                try:
                    add_book(title, author, isbn, int(copies))
                    st.success("Book added")
                except Exception as e:
                    st.error(str(e))
            else:
                st.error("All fields are required")
    st.divider()
    st.header("Manage Books")
    book_list = get_books()
    if not book_list:
        st.info("No books yet")
    else:
        options = {format_book_option(b): b["id"] for b in book_list}
        selected_label = st.selectbox("Select a book", list(options.keys()))
        selected_id = options[selected_label]
        selected_book = get_book_by_id(selected_id)
        ac = get_available_copies(selected_id)
        st.caption(f'Available copies: {ac} of {selected_book["total_copies"]}')
        c1, c2 = st.columns(2)
        with c1:
            with st.form("edit_book"):
                nt = st.text_input("Title", value=selected_book["title"])
                na = st.text_input("Author", value=selected_book["author"])
                ni = st.text_input("ISBN", value=selected_book["isbn"])
                nc = st.number_input("Total copies", min_value=0, step=1, value=int(selected_book["total_copies"]))
                upd = st.form_submit_button("Update")
                if upd:
                    try:
                        update_book(selected_id, nt, na, ni, int(nc))
                        st.success("Book updated")
                    except Exception as e:
                        st.error(str(e))
        with c2:
            if st.button("Delete Book", type="primary"):
                try:
                    delete_book(selected_id)
                    st.success("Book deleted")
                except Exception as e:
                    st.error(str(e))
    st.divider()
    st.subheader("All Books")
    if book_list:
        st.table(book_list)

elif section == "Members":
    st.header("Add Member")
    with st.form("add_member"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        submitted = st.form_submit_button("Add")
        if submitted:
            if name and email:
                try:
                    add_member(name, email, phone)
                    st.success("Member added")
                except Exception as e:
                    st.error(str(e))
            else:
                st.error("Name and email are required")
    st.divider()
    st.header("Manage Members")
    member_list = get_members()
    if not member_list:
        st.info("No members yet")
    else:
        options = {format_member_option(m): m["id"] for m in member_list}
        selected_label = st.selectbox("Select a member", list(options.keys()))
        selected_id = options[selected_label]
        selected_member = get_member_by_id(selected_id)
        c1, c2 = st.columns(2)
        with c1:
            with st.form("edit_member"):
                nn = st.text_input("Name", value=selected_member["name"])
                ne = st.text_input("Email", value=selected_member["email"])
                np = st.text_input("Phone", value=selected_member["phone"] or "")
                upd = st.form_submit_button("Update")
                if upd:
                    try:
                        update_member(selected_id, nn, ne, np)
                        st.success("Member updated")
                    except Exception as e:
                        st.error(str(e))
        with c2:
            if st.button("Delete Member", type="primary"):
                try:
                    delete_member(selected_id)
                    st.success("Member deleted")
                except Exception as e:
                    st.error(str(e))
    st.divider()
    st.subheader("All Members")
    if member_list:
        st.table(member_list)

elif section == "Loans":
    st.header("Borrow Book")
    members = get_members()
    books = get_books()
    if not members or not books:
        st.info("Add members and books first")
    else:
        m_options = {format_member_option(m): m["id"] for m in members}
        b_options = {format_book_option(b): b["id"] for b in books}
        m_label = st.selectbox("Member", list(m_options.keys()))
        b_label = st.selectbox("Book", list(b_options.keys()))
        m_id = m_options[m_label]
        b_id = b_options[b_label]
        ac = get_available_copies(b_id)
        st.caption(f"Available copies: {ac}")
        due = st.date_input("Due date", value=date.today())
        if st.button("Borrow"):
            try:
                borrow_book(m_id, b_id, due)
                st.success("Loan created")
            except Exception as e:
                st.error(str(e))
    st.divider()
    st.header("Active Loans")
    loans = get_loans(active_only=True)
    if not loans:
        st.info("No active loans")
    else:
        st.table(loans)
        loan_ids = {f'Loan #{l["id"]} — member {l["member_id"]} book {l["book_id"]}': l["id"] for l in loans}
        lbl = st.selectbox("Select a loan to return", list(loan_ids.keys()))
        lid = loan_ids[lbl]
        if st.button("Return"):
            try:
                return_book(lid)
                st.success("Book returned")
            except Exception as e:
                st.error(str(e))
    st.divider()
    st.header("Overdue")
    overdue = get_overdue()
    if overdue:
        st.table(overdue)
    else:
        st.info("No overdue loans")

