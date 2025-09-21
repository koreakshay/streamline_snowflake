# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col, when_matched
import pandas as pd

# Write directly to the app
st.title(f":cup_with_straw: Customize your own smoothie :cup_with_straw:")
st.write(
  """
  Choose the fruits you want in custom smoothie! :yum:
  """
)

name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()

ingredient_list = st.multiselect(
    "Choose upto 5 fruits",
    my_dataframe,
    max_selections = 5
)

if ingredient_list:
    ingredients_string = ''

    for fruit_chosen in ingredient_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
      
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    st.write(my_insert_stmt)
    st.stop()
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('You smoothie is ordered!', icon="✅")


