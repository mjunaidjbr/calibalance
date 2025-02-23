from flask import Flask, render_template, redirect, url_for, request, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
import os
app = Flask(__name__)
app.secret_key = 'supersecretkey'
DATABASE = os.path.join(os.path.dirname(__file__), 'calories_calculator.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def setup():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                      )''')
        db.execute('''CREATE TABLE IF NOT EXISTS calories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        date DATE,
                        daily_calories INTEGER,
                        consumed_calories INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                      )''')
        # db.execute('''DROP TABLE IF EXISTS food''')
        # db.execute('''CREATE TABLE IF NOT EXISTS food (
        #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
        #                 name TEXT NOT NULL,
        #                 calories INTEGER NOT NULL,
        #                 protein INTEGER,
        #                 carbs INTEGER,
        #                 fats INTEGER,
        #                 category TEXT,
        #                 image_url TEXT,
        #                 description TEXT
        #               )''')
        db.execute('''INSERT INTO food (name, calories, protein, carbs, fats, category, image_url, description)
               VALUES
               ('Grilled Chicken Breast', 165, 31, 0, 3.6, 'Protein', 'grilled-chicken.jpg', 'A high-protein, low-fat meal perfect for muscle building and weight management.'),
               ('Salmon Fillet', 206, 22, 0, 12, 'Protein', 'salmon.jpg', 'Rich in omega-3 fatty acids and protein, salmon is great for heart health and brain function.'),
               ('Quinoa Salad', 222, 8, 39, 3.6, 'Vegetarian', 'quinoa-salad.jpg', 'A balanced meal packed with fiber, protein, and essential nutrients for a healthy diet.'),
               ('Greek Yogurt with Honey', 100, 10, 12, 0, 'Snack', 'greek-yogurt.jpg', 'A probiotic-rich snack that supports digestion and provides a natural energy boost.'),
               ('Mixed Vegetable Stir-Fry', 150, 6, 30, 1, 'Vegetarian', 'vegetable-stirfry.jpg', 'Loaded with vitamins and antioxidants, a perfect side dish for a healthy meal.'),
               ('Oatmeal with Berries', 154, 6, 27, 3.5, 'Breakfast', 'oatmeal.jpg', 'A fiber-rich breakfast that keeps you full and helps regulate blood sugar levels.'),
               ('Egg White Omelette', 120, 24, 2, 2, 'Breakfast', 'egg-white-omelette.jpg', 'A lean protein-packed breakfast that supports muscle recovery and fat loss.'),
               ('Avocado Toast', 220, 5, 24, 15, 'Snack', 'avocado-toast.jpg', 'A healthy, nutrient-dense snack loaded with healthy fats and fiber.'),
               ('Tofu Stir-Fry', 180, 15, 10, 8, 'Vegetarian', 'tofu-stirfry.jpg', 'A plant-based protein meal with veggies and tofu, rich in antioxidants and healthy fats.'),
               ('Chicken Caesar Salad', 350, 30, 12, 20, 'Protein', 'chicken-caesar-salad.jpg', 'A classic salad with grilled chicken, Caesar dressing, and a blend of crunchy greens.'),
               ('Cottage Cheese with Pineapple', 120, 14, 10, 2, 'Snack', 'cottage-cheese.jpg', 'A sweet and tangy snack, perfect for a protein boost and digestive health.'),
               ('Beef Stir-Fry', 270, 30, 12, 15, 'Protein', 'beef-stirfry.jpg', 'A high-protein, savory dish with tender beef and colorful vegetables.'),
               ('Lentil Soup', 180, 12, 30, 3, 'Vegetarian', 'lentil-soup.jpg', 'A hearty and filling soup loaded with fiber and plant-based protein.'),
               ('Sweet Potato and Black Bean Bowl', 350, 15, 50, 8, 'Vegetarian', 'sweet-potato-black-bean.jpg', 'A hearty bowl of roasted sweet potatoes, black beans, and healthy spices.'),
               ('Turkey Wrap', 250, 28, 20, 8, 'Protein', 'turkey-wrap.jpg', 'A lean and protein-rich wrap filled with turkey, vegetables, and light dressing.'),
               ('Chia Pudding', 210, 6, 18, 10, 'Snack', 'chia-pudding.jpg', 'A nutrient-packed dessert made from chia seeds, rich in omega-3s and fiber.'),
               ('Grilled Shrimp Skewers', 220, 23, 1, 14, 'Protein', 'grilled-shrimp.jpg', 'A delicious and low-carb seafood option, perfect for a protein boost.'),
               ('Stuffed Bell Peppers', 250, 18, 20, 12, 'Protein', 'stuffed-bell-peppers.jpg', 'Bell peppers stuffed with lean ground meat, rice, and spices for a filling meal.'),
               ('Baked Cod with Lemon', 150, 32, 0, 2, 'Protein', 'baked-cod.jpg', 'A light and flaky fish dish with a tangy lemon flavor, rich in lean protein.'),
               ('Spinach and Feta Omelette', 200, 18, 4, 12, 'Breakfast', 'spinach-omelette.jpg', 'A nutrient-dense breakfast packed with protein, iron, and healthy fats.'),
               ('Brown Rice and Black Beans', 250, 10, 45, 3, 'Vegetarian', 'brown-rice-black-beans.jpg', 'A fiber-rich meal providing plant-based protein and essential minerals.'),
               ('Almond Butter Banana Toast', 280, 7, 35, 14, 'Snack', 'almond-butter-toast.jpg', 'A satisfying snack with a balance of healthy fats, fiber, and natural sweetness.'),
               ('Grilled Zucchini and Quinoa Bowl', 300, 12, 40, 8, 'Vegetarian', 'zucchini-quinoa-bowl.jpg', 'A wholesome bowl with grilled zucchini, quinoa, and a light dressing.')
            ''')


        db.commit()


@app.before_request
def before_request():
    open_routes = ['login', 'signup', 'static']  # Allow these pages
    if request.endpoint not in open_routes and 'username' not in session:
        return redirect(url_for('login'))
    
    # Prevent logged-in users from seeing login/signup pages
    if request.endpoint in ['login', 'signup'] and 'username' in session:
        return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        try:
            db = get_db()
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return 'Username already exists', 409
    return render_template('signup.html')

@app.route('/food-suggestions')
def food_suggestions():
    db = get_db()
    # Fetch food data and saved calories for the last 7 days for the logged-in user
    user = query_db('SELECT id FROM users WHERE username = ?', [session['username']], one=True)
    if not user:
        return jsonify({'message': 'User not found', 'status': 'error'}), 404

    user_id = user[0]
    today = datetime.now()
    start_date = today - timedelta(days=6)  # 7-day period including today

    # Fetch saved calories for each day in the last 7 days
    calorie_data = query_db('''
        SELECT date, daily_calories 
        FROM calories 
        WHERE user_id = ? AND date >= ? 
        ORDER BY date
    ''', [user_id, start_date.strftime('%Y-%m-%d')])

    # Create a dictionary to store the calories by date for easy lookup
    calorie_dict = {record[0]: record[1] for record in calorie_data}

    # Fetch random food suggestions (6 food items)
    food_data = db.execute('SELECT * FROM food ORDER BY RANDOM() LIMIT 21').fetchall()

    food_items = []
    for row in food_data:
        food_items.append({
            'id': row[0],
            'name': row[1],
            'calories': row[2],
            'protein': row[3],
            'carbs': row[4],
            'fats': row[5],
            'category': row[6],
            'image_url': row[7],
            'description': row[8]
        })
    
    # Add daily calories to each food item based on the day of the suggestion
    for index, food_item in enumerate(food_items):
        day = (today + timedelta(days=index)).strftime('%Y-%m-%d')
        food_item['saved_calories'] = calorie_dict.get(day, 'No data')  # Add saved calories for each day

    return render_template('food_suggestions.html', food_items=food_items)



@app.route('/calories-adjustments', methods=['GET', 'POST'])
def calories_adjustments():
    user = query_db('SELECT * FROM users WHERE username = ?', [session['username']], one=True)
    if not user:
        return redirect(url_for('login'))

    user_id = user[0]
    today = datetime.now().strftime('%Y-%m-%d')

    # Fetch the last 7 days' calorie records
    start_date = datetime.now() - timedelta(days=6)
    records = query_db('''
        SELECT id, date, daily_calories, consumed_calories 
        FROM calories 
        WHERE user_id = ? AND date >= ? 
        ORDER BY date ASC
    ''', [user_id, start_date.strftime('%Y-%m-%d')])

    if request.method == 'POST':
        consumed_calories = int(request.form['consumed_calories'])

        db = get_db()
        remaining_to_deduct = consumed_calories

        for record in records:
            record_id, date, daily_calories, consumed = record
            available_calories = daily_calories - consumed  # Remaining calories for the day

            if remaining_to_deduct > available_calories:
                # Use up all available calories for this day and move to the next day
                db.execute('''
                    UPDATE calories 
                    SET consumed_calories = ? 
                    WHERE id = ?
                ''', (daily_calories, record_id))
                remaining_to_deduct -= available_calories  # Deduct used calories from remaining
            else:
                # Deduct remaining calories and stop
                db.execute('''
                    UPDATE calories 
                    SET consumed_calories = consumed_calories + ? 
                    WHERE id = ?
                ''', (remaining_to_deduct, record_id))
                remaining_to_deduct = 0
                break  # Stop once all calories are deducted

        db.commit()
        return redirect(url_for('calories_adjustments'))  # Reload page after update

    return render_template('calories_adjustments.html', records=records)


@app.route('/save_calories', methods=['POST'])
def save_calories():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in', 'status': 'error'}), 401

    data = request.get_json()
    daily_calories = data.get('daily_calories', '0').replace(',', '')  # Remove commas
    if not daily_calories.isdigit() or int(daily_calories) <= 0:
        return jsonify({'message': 'Invalid calorie value', 'status': 'error'}), 400

    user = query_db('SELECT id FROM users WHERE username = ?', [session['username']], one=True)
    if not user:
        return jsonify({'message': 'User not found', 'status': 'error'}), 404

    user_id = user[0]
    today = datetime.now()
    start_date = today - timedelta(days=6)  # 7-day period including today

    db = get_db()

    # Fetch records within the last 7 days
    existing_records = query_db('''
        SELECT date FROM calories 
        WHERE user_id = ? AND date >= ?
    ''', [user_id, start_date.strftime('%Y-%m-%d')])

    existing_dates = {record[0] for record in existing_records}  # Convert to set for quick lookup

    for i in range(7):
        date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        if date in existing_dates:
            # Update existing record and reset consumed_calories to 0
            db.execute('''
                UPDATE calories SET daily_calories = ?, consumed_calories = 0
                WHERE user_id = ? AND date = ?
            ''', (int(daily_calories), user_id, date))
        else:
            # Insert new record
            db.execute('''
                INSERT INTO calories (user_id, date, daily_calories, consumed_calories) 
                VALUES (?, ?, ?, 0)
            ''', (user_id, date, int(daily_calories)))

    db.commit()

    return jsonify({'message': 'Calories saved/updated successfully for the last 7 days!', 'status': 'success'}), 200


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    setup()
    # seed_food_data()
    app.run(debug=False)