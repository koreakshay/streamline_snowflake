import streamlit as st
from snowflake.snowpark import Row

st.set_page_config(page_title="Smoothie Orders", page_icon="🥤")
st.title("Smoothie Order Form")

# ——— Connection (built-in Streamlit Snowflake connection) ———
# Requires [connections.snowflake] in Secrets (see below).
conn = st.connection("snowflake")                     # built-in
session = conn.session()                              # Snowpark session
# Docs: st.connection + session() examples. 
# https://docs.streamlit.io/develop/api-reference/connections/st.connections.snowflakeconnection

# ——— UI ———
name_on_order = st.text_input("Name on Smoothie")
if name_on_order:
    st.write("The name on the smoothie will be:", name_on_order)

# Pull fruit options from Snowflake (expects a table smoothies.public.fruit_options with FRUIT_NAME)
fruit_rows = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select("FRUIT_NAME")
    .sort("FRUIT_NAME")
    .collect()
)
fruit_options = [r["FRUIT_NAME"] for r in fruit_rows]

ingredients_list = st.multiselect("Pick your ingredients", fruit_options)

# ——— Submit ———
if st.button("Submit Order", disabled=not (name_on_order and ingredients_list)):
    # Ensure a target table exists (2 columns: ingredients, name_on_order)
    session.sql("""
        CREATE TABLE IF NOT EXISTS SMOOTHIES.PUBLIC.ORDERS (
          ID NUMBER AUTOINCREMENT,
          NAME_ON_ORDER STRING,
          INGREDIENTS STRING,
          CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """).collect()

    # Join ingredients in Python (don’t use '+' in SQL for strings)
    ingredients_string = ",".join(ingredients_list)

    # Safe insert via Snowpark (avoids quoting/binding issues)
    session.table("SMOOTHIES.PUBLIC.ORDERS").insert(
        Row(name_on_order=name_on_order, ingredients=ingredients_string)
    )

    st.success(f"Your smoothie is ordered, {name_on_order} ✅")
