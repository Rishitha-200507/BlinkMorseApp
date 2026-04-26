import customtkinter as ctk


def open_sign_module(app):

    app.clear_window()

    app.sidebar = ctk.CTkFrame(app, width=220)
    app.sidebar.pack(side="left", fill="y")

    ctk.CTkLabel(
        app.sidebar,
        text="Sign Module",
        font=("Arial", 28, "bold")
    ).pack(pady=25)

    ctk.CTkButton(
        app.sidebar,
        text="Dashboard",
        width=180
    ).pack(pady=10)

    ctk.CTkButton(
        app.sidebar,
        text="Translator",
        width=180
    ).pack(pady=10)

    ctk.CTkButton(
        app.sidebar,
        text="Learning",
        width=180
    ).pack(pady=10)

    ctk.CTkButton(
        app.sidebar,
        text="Change Module",
        width=180,
        command=app.show_module_page
    ).pack(pady=10)

    ctk.CTkButton(
        app.sidebar,
        text="Logout",
        width=180,
        fg_color="red",
        command=app.show_login_page
    ).pack(pady=30)

    app.main_frame = ctk.CTkFrame(app)
    app.main_frame.pack(
        side="right",
        fill="both",
        expand=True
    )

    ctk.CTkLabel(
        app.main_frame,
        text="Sign Language Module",
        font=("Arial", 34, "bold")
    ).pack(pady=40)