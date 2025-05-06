
# 🛒 Flask Product Manager - tameronline-pro_product

A simple and professional product management system built with Python and Flask. It includes an admin panel, public product listing, image uploads, and SQLite-based storage.

---

## ✅ Main Features

- 🔐 Admin dashboard with login protection
- ➕ Add products with image, description, specs, and price
- 🖼️ Upload and store product images in `static/uploads/`
- 📝 View product details on a separate page
- 🗂️ Admin page to manage (edit/delete) all products
- 🧹 Button to reset the entire database
- 🌐 Fully Arabic user interface with clean design

---

## 📁 Project Structure

```
tameronline-pro_product/
├── myapp.py              # Main application entry point
├── config.py             # App configuration
├── requirements.txt      # Required packages
├── instance/products.db  # SQLite database
├── models/               # Product model definition
├── routes/               # Admin and user routes
├── templates/            # HTML templates for both admin and user views
├── static/               # CSS and image uploads
├── utils/logic/          # Helper modules (currently empty)
└── .env                  # (Optional) Environment variables
```

---

## ⚙️ Running Locally

### 1. Clone the Repository:

```bash
git clone https://github.com/your-username/tameronline-pro_product.git
cd tameronline-pro_product
```

### 2. Create a Virtual Environment and Install Dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Environment Variables:

Create a `.env` file with the following:

```env
cv_kay=your_secret_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password
```

### 4. Run the App:

```bash
python myapp.py
```

Open [http://localhost:8030](http://localhost:8030) in your browser.

---

## 🔐 Admin Login

- Username: as set in `ADMIN_USERNAME` in `.env`
- Password: as set in `ADMIN_PASSWORD` in `.env`

---

## 🗃️ Notes

- Uses SQLite for local development
- Images are saved under `static/uploads/` with unique names
- Only valid image formats are accepted (png, jpg, jpeg, webp)
- No categories, search, or API support yet

---

## 📌 Future Improvements

- ✅ Add product categories
- ✅ Implement search functionality
- ✅ Create a RESTful API
- ✅ Add Contact/About pages
- ✅ Enable notifications (e.g., email)
- ✅ Deploy to PythonAnywhere / Render

---

## 📄 License

Open-source for personal and educational use.
