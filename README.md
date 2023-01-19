<h1 style="color:rgb(133, 24, 24); text-align:center">Django Pizza Delivery App</h1>

<h1>Live Demo</h1>
<a href="http://notarious2.pythonanywhere.com/">Visit</a> http://notarious2.pythonanywhere.com/

<img src="images/front_page.png" alt="Front page"/>

<h3>Admin credentials:</h3>

<p>http://notarious2.pythonanywhere.com/admin/</p>

```
login: bekzod
password: bekzod
```

<hr>
<p style="font-weight: bold;">This e-commerce app was built using the following technologies:</p>
<p float="left">
<img src="images/django.jpeg" style="width:100px; height: 50px; border-radius: 100px;" alt="Django">
<img src="images/tailwindcss.svg" style="width:200px; height: 30px;" alt="TailwindCSS">
<img src="images/stripe.webp" style="width:100px; height: 50px;" alt="Stripe">
<img src="images/jquery.svg" style="width:120px; height: 40px;" alt="JQuery">

</p>
<h1>Features</h1>
<ul>
    <li>
        <p>Customer Registration, Login and Logout</p>
    </li>
    <li>
        <p>Customer and Guest Checkout (using device ID set in Cookies) </p>
    </li>
    <li>
        <p>Delivery and Carry-out option</p>
    </li>
    <li>
        <p>Registered users can see completed orders</p>
    </li>
    <li>
        <p>Deferred <strong>Cash</strong> payment and Instant online payment with <strong>Stripe</strong></p>
    </li>

</ul>

<h1>SQL Relational Schema</h1>
<p>The app uses SQLite database. Relational representation of Django Models used in ePizza app are provided below. </p>
<p>Link to the diagram in <a href="https://drawsql.app/teams/bekzods-team-1/diagrams/epizza-django">drawSQL.app</a></p>
<img src="images/sql_schema.png" alt="SQL model"/>

<h1>Coupons</h1>
<p>3 coupons (integrated with Stripe Payment Gateway) are available at Checkout </p>

**WINTER:** 50% off the order total

**SPRING:** 20% off the order total

**SUMMER:** $10 off the order total

<h1>App Setup</h1>

**Clone Repository:**

```
git clone https://github.com/notarious2/Django-Pizza-Delivery.git
cd Django-Pizza-Delivery
```

**Configure Enviornmental variables:**
<br>
_inside 'epizza' folder add .env file and add Secret Key, Stripe Publishable Key and Stripe Secret Key_

```
SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
```

**Create and Activate Virtual Environment:**

```
virtualenv env
env\Scripts\activate
```

**Install Dependencies:**

```
pip install -r requirements.txt
```

**Run Development Server:**

```
python manage.py runserver
```

<h1>Tailwind CSS Setup</h1>

_You must have Node.js installed in your PC_
<br>
_Tailwind Directives are in store/static/store/src/input.css_
<br>
_Ouput (autogenerated) stored in store/static/store/src/styles.css_

**Install Dependencies:**

```
npm install
```

**Start Tailwind CLI build process**

runs: "tailwind build -i store/static/store/src/input.css -o store/static/store/src/styles.css --watch" <strong>Script</strong> inside <strong>package.json</strong>

```
npm run build
```
