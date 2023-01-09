<h1 style="color:rgb(133, 24, 24); text-align:center">Django Pizza Delivery App</h1>

<h1><a href="">Demo</a></h1>

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
        <p>Deferred <strong>Cash</strong> payment and Instant online payment with Stripe</p>
    </li>

</ul>

<h1>SQL Relational Schema</h1>
<p>The app uses SQLite database. Relational representation of Django Models used in ePizza app are provided below. </p>
<p>Link to the diagram in <a href="https://drawsql.app/teams/bekzods-team-1/diagrams/epizza-django">drawSQL.app</a></p>
<img src="images/sql_schema.png" alt="SQL model"/>

<h3>App Set-Up</h3>
<ul>
    <li>
        <div>
            <p style="font-weight:600;">Clone Repository:</p>
            <p style="color:rgb(24, 24, 213)">git clone https://github.com/notarious2/Django-Pizza-Delivery.git</p>
            <p style="color:rgb(24, 24, 213)">cd Django-Pizza-Delivery</p>
        </div>
    </li>
    <li>
        <div>
            <p style="font-weight:600;">Create and Activate virtual environment:</p>
            <p style="color:rgb(24, 24, 213)">virtualenv env</p>
            <p style="color:rgb(24, 24, 213)">env\Scripts\activate</p>
        </div>
    </li>
    <li>
        <div>
            <p style="font-weight:600;">Install Dependencies:</p>
            <p style="color:rgb(24, 24, 213)">pip install -r requirements.txt</p>
        </div>
    </li>
    <li>
        <div>
            <p style="font-weight:600;">Run Development Server:</p>
            <p style="color:rgb(24, 24, 213)">python manage.py runserver</p>
        </div>
    </li>
</ul>
