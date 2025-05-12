from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Product(db.Model):
    """Database model for products.

    Attributes:
        id (int): Primary key.
        name (str): Name of the product.
        price (float): Price of the product.
        description (str): Product description.
        image (str): URL or path to the product image.
        specs (str): Specifications of the product.
        product_code (str): Unique code identifying the product.
        merchant_id (int): Foreign key to the User (merchant).
        is_approved (bool): Approval status of the product.
        updated_at (datetime): Last update timestamp.
    """

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    specs = db.Column(db.Text)
    product_code = db.Column(db.String(30), unique=True, nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)  # Set default approval as False
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the product."""
        return f'<Product {self.name}>'

    def generate_code(self, sequence):
        """Generate a unique product code based on merchant ID and sequence."""
        if self.merchant_id:
            self.product_code = f"USR{self.merchant_id:06d}-PRO{sequence:03d}"


class User(db.Model):
    """Database model for users.

    Attributes:
        id (int): Primary key.
        email (str): User's email address.
        username (str): Unique username.
        password_hash (str): Hashed password.
        role (str): Role of the user (e.g., user, admin).
        products (list): List of products associated with the user.
        created_at (datetime): Account creation timestamp.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), default='user')
    products = db.relationship('Product', backref='merchant', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Generate and store a password hash.

        Args:
            password (str): The plaintext password to hash.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the provided password against the stored hash.

        Args:
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Return a string representation of the user."""
        return f'<User {self.username}>'


class Notification(db.Model):
    """Database model for notifications.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the user.
        role (str): Role of the user to notify (admin, merchant, customer, visitor).
        type (str): Type of notification (info, success, error).
        message (str): Notification message.
        product_id (int): Foreign key to the associated product.
        order_id (int): Optional foreign key to the associated order.
        is_read (bool): Status of whether the notification has been read.
        is_visible (bool): Status of whether the notification is visible.
        created_at (datetime): Timestamp of when the notification was created.
    """

    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # admin, merchant, customer, visitor
    type = db.Column(db.String(50), nullable=False, default='info')  # Default type is 'info'
    message = db.Column(db.Text, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    order_id = db.Column(db.Integer, nullable=True)
    is_read = db.Column(db.Boolean, default=False)  # Default is unread
    is_visible = db.Column(db.Boolean, default=True)  # Default is visible
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the notification."""
        return f"<Notification {self.id} to {self.role} ({self.type})>"
