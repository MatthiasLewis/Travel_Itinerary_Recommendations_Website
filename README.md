<h1>Travel Itinerary Recommendations Website</h1>
<h2>Summary</h2>
<p>In this project, Python is used as the main programming language, with MySQL, SQLite, and Redis as the databases or caching tools for data access, and the results are presented on a website. With user-inputted locations, dates, and various travel preferences, a backend algorithm is employed to provide a personalized itinerary for travelers facing decision-making difficulties.</p>

<h3>Imported Modules and Libraries</h3>
<ul>
    <li><code>create_engine</code> is a method from the <code>sqlalchemy</code> library used to connect to the database.</li>
    <li><code>MethodResource</code> is an object that can capture the content of request and response methods.</li>
    <li><code>marshal_with</code>, <code>doc</code>, <code>use_kwargs</code> help organize and format textual data for presentation.</li>
    <li><code>jsonify</code> is used to convert the response content format to JSON data format.</li>
    <li><code>redis</code> is a type of database that runs in memory and allows setting data expiration times, used for caching to save data retrieval time.</li>
    <li><code>inspect</code> is a method for retrieving database structure information, providing access to table structure details (similar to MySQL's <code>DESCRIBE tablename</code>), database engine information (such as PostgreSQL version), triggers, or index information. In this project, it is mainly used to obtain table structure details.</li>
    <li><code>datetime</code> is used to convert retrieved date and day information to datetime format and obtain day-of-week information.</li>
    <li><code>sklearn</code> is an abbreviation for scikit-learn, a machine learning library. In this project, it is mainly used for clustering and haversine distance calculations.</li>
</ul>
<h2>main.py</h2>
<h3>Avoid Encoding Issues</h3>
<p>Use <code>app.config['JSON_AS_ASCII'] = False</code> to avoid encoding issues and ensure the correct data format is delivered to the web client with <code>response.headers['Content-Type'] = 'application/json; charset=utf-8'</code>.</p>

<h3>Evolution of Database Reading Design</h3>
<p>In the initial design, the backend directly retrieved data from MySQL for computation, but this approach proved to be too slow. After various adjustments, the final approach involves storing data in MySQL, temporary storage in SQLite, and caching in Redis.</p>
<li>Access only from <code>mysql</code>: Data retrieval and computation took approximately 6-10 seconds.</li>
<li>Access only from <code>sqlite</code>: Data retrieval and computation were faster, saving approximately 3 seconds compared to the previous approach.</li>
<li>Access from <code>sqlite</code> with <code>redis</code> caching (without caching before computation): Similar to the previous approach in terms of time.</li>
<li>Access from <code>sqlite</code> with <code>redis</code> caching (with caching before computation): Approximately 2 seconds faster than the previous approach.</li>
<p>Below is the code for caching before entering the computation API.</p>
<pre>
<code class="language-python">
    @doc(description='Get travel itinerary info.', tags=['get'])
    @use_kwargs(travel_tinerary_model.travelPostSchema, location="query")
    @marshal_with(travel_tinerary_model.travelPostResponse, code=204)
    @app.route("/Travel", methods=["GET"])
    def get():
        import redis, json
        start_time = time.time()
        from sqlalchemy import create_engine, inspect

        city = request.args.get("county")
        engine = create_engine("sqlite:///travel.db?charset=utf8")

        with engine.connect() as con:
            index1 = 1
            for i in ["food_v3", "hotel_v1", "viewpoint_v3", "food_rest_day_0802", "food_rest_interval"]:
                if index1 <= 3:
                    query = f"select * from {i} where city = '{city}'"
                else:
                    query = f"select * from {i} where address LIKE '%{city}%'"
                rows = con.execute(query).fetchall()
                # SQLite column retrieval syntax
                inspector = inspect(engine)
                columns = inspector.get_columns(i)
                # SQLite
                keytag = [n["name"] for n in columns]
                redis_hash = []
                for row in rows:
                    # Organize data into a dictionary
                    redis_item = dict(zip(keytag, row))
                    redis_hash.append(redis_item)
                # Connect to Redis
                pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
                r = redis.Redis(connection_pool=pool)
                # Write data to Redis
                r.hset(i, city, json.dumps(redis_hash))
                # Set expiration time (in seconds)
                expiration_time = 600  # 10 minutes
                r.expire(i, expiration_time)
                index1 += 1

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Program execution time: {elapsed_time:.6f} seconds")

        return ("", 204)
</code>
</pre>

<h2>mainrun.py</h2>
<p>Main code for running the entire algorithm.</p>
<h3>Connect to Redis</h3>
<p>Retrieve data from Redis and combine latitude and longitude fields in the data to create a GeoDataFrame with geographical information.</p>
<pre>
<code class="language-python">
    # Database
    # Connect to Redis
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
    r = redis.Redis(connection_pool=pool)

    df_viewpoint = pd.DataFrame(json.loads(r.hget("viewpoint_v3", pref['county'])))
    df_viewpoint = gpd.GeoDataFrame(df_viewpoint, crs="EPSG:4326", geometry=[Point(lnglat) for lnglat in zip(df_viewpoint['lng'], df_viewpoint['lat'])])

    df_food = pd.DataFrame(json.loads(r.hget("food_v3", pref['county'])))
    df_food = gpd.GeoDataFrame(df_food, crs="EPSG:4326", geometry=[Point(lnglat) for lnglat in zip(df_food['lng'], df_food['lat'])])

    df_hotel = pd.DataFrame(json.loads(r.hget("hotel_v1", pref['county'])))
    df_hotel = gpd.GeoDataFrame(df_hotel, crs="EPSG:4326", geometry=[Point(lnglat) for lnglat in zip(df_hotel['lng'], df_hotel['lat'])])
</code>
</pre>

<h3>Score and Weight Calculations</h3>
<p>Assign scores to data using a predefined algorithm and set score weights based on importance.</p>
<pre>
<code class="language-python">
    # Assign scores to hotels
    df_hotel['like_score'] = calculate_tag_score_2(df_hotel['keyword'], pref["hotel_like_tag"])
    df_hotel['price_score'] = calculate_hotel_score_2(df_hotel['lower_price'], df_hotel['ceiling_price'],  pref['hotel_price_tag']) # ***
    df_hotel['other_score'] = calculate_tag_score_2(df_hotel['tag'], pref["hotel_other_tag"])/5  # Additional services have a lower weight # ***

    # Calculate overall hotel scores
    df_hotel['overall_score'] = df_hotel['like_score'] + df_hotel['price_score'] + df_hotel['other_score']

    # Assign scores to food
    df_food['taste_score'] = calculate_tag_score_2(df_food['taste_tag'], pref["food_taste_tag"])
    df_food['price_score'] = calculate_price_score_3(df_food['price_level'], pref['food_price_tag'])
    df_food['other_score'] = calculate_tag_score_2(df_food['other_tag'], pref["food_other_tag"])*10  # High weight for essential requirements # ***

    # Calculate overall food scores
    df_food['overall_score'] = df_food['taste_score'] + df_food['price_score'] + df_food['other_score']

    # Assign scores to viewpoints
    df_viewpoint['other_score'] = calculate_tag_score_2(df_viewpoint['tag'], pref["viewpoint_other_tag"])

    # Calculate overall viewpoint scores
    df_viewpoint['overall_score'] = df_viewpoint['other_score']
</code>
</pre>

<h3>Data Clustering</h3>
<p>Cluster data based on geographical location to avoid planning activities that are too far apart for the same day.</p>
<pre>
<code class="language-python">
    # Calculate distance matrix
    haversine_matrix = haversine_distances(
        geo_df[['lat_rad', 'lng_rad']].values,
        geo_df[['lat_rad', 'lng_rad']].values
    ) * 6371000.0  # 6371000.0 is Earth's radius in meters

    # Apply DBSCAN for clustering
    dbscan = DBSCAN(eps=2000, min_samples=3, metric='precomputed')
    geo_df['cluster'] = dbscan.fit_predict(haversine_matrix)
</code>
</pre>

<h3>Check Cluster Quantity</h3>
<p>If the number of clusters in the selected locations is less than the number of days for the trip, fill the shortfall with the largest cluster.</p>
<pre>
<code class="language-python">
    # Check the quantity of clusters
    while len(largest_clusters) < n:
        # Allocate all days to the largest cluster
        largest_clusters = largest_clusters.insert(0, largest_clusters[0])
        #print(largest_clusters)
</code>
</pre>
