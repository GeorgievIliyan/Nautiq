"""
# Nautiq 🚤

Nautiq is a web application that combines an interactive map with community-sourced information. Users can log beach conditions and discover new locations. The platform automatically generates tasks to encourage active participation. Through points, leaderboards, and achievements, Nautiq maintains user engagement and fosters a dynamic community. This sets it apart from competitors like Beachday or SwimGuide, which provide information but lack gamification and social interaction.

---

## 📚 Table of Contents

- About
- Features
- Installation
- Usage
- Contributing
- License
- About the competition
- Contact

---

## 🔹 About

Nautiq is designed to offer a fast and easy way to manage coastal data, optimize exploration, and visualize locations on an interactive map. The platform encourages community engagement and gamifies the beach discovery experience, making it both informative and fun.

---

## ✨ Features

- Local Django server for testing
- Database migrations with pre-configured scripts
- Configuration via .env file
- Preparation for integration with mapping services (Jawg Maps)
- Community-driven data input
- Gamification: points, leaderboards, achievements

---

## 🛠 Installation

Follow these steps to run Nautiq locally:

1. Clone the repository:
git clone https://github.com/GeorgievIliyan/Nautiq

2. Create a virtual environment:  
    ``` bash
    python -m venv venv
    ```
3. Activate the virtual environment:
    ``` bash
    venv\Scripts\activate
    ```
4. Install dependencies:  
    ``` bash
    pip install -r requirements.txt
    ```
5. Configure environment variables:
Create a .env file in the project root with the following content:  
    ``` env
    DJANGO_SECRET_KEY=<your-key>  
    ENVIRONMENT=production  
    JAWG_ACCESS_TOKEN=  
    ```
💡 Notes:
- ```DJANGO_SECRET_KEY``` – for local testing, you can use any random string.
- ```JAWG_ACCESS_TOKEN``` – needed for integration with Jawg Maps; token can be generated via the official Jawg website: https://www.jawg.io/en/

6. Open the project in your preferred code editor.

7. Run initial migrations:  
    ``` bash
    python manage.py makemigrations
    ```

8. Apply migrations to the database:
    ``` bash
    python manage.py migrate
    ```

9. Start the local server:
    ```bash
    python manage.py runserver
    ```

10. You should see:
Starting development server at ```http://127.0.0.1:8000/```

11. Open your browser and visit:
```http://127.0.0.1:8000```

---

## 🚀 Usage

Once the server is running, you can explore Nautiq locally, add data, and test its features.

---

## 🤝 Contributing

To contribute:

1. Fork the repository
2. Create a new branch (git checkout -b feature/YourFeature)
3. Make your changes
4. Submit a Pull Request

---

## 📄 License

This project is licensed under the GNU-GPL-3 license. Open []

---

## 🏁 About the competiton
5/20-th place in the *National Autumn Tournament in Information Technology 'John Atanasoff'* (НЕТИТ "Джон Атанасов") in Bulgaria for grades IIX - X, software apps.
72/100 points.

## 📬 Contact

Iliyan Georgiev – @GeorgievIliyan  
Project: https://github.com/GeorgievIliyan/Nautiq