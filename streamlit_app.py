import os
import io
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Sheets API scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Spreadsheet ID and range
SPREADSHEET_ID = "154vMLqaYr25uV4zStxUgTk0TDsT7e26DKQjrRscEERo"
RANGE_NAME = 'Sheet1!A1:Q501'

def get_sheet_data():
    """Fetches data from Google Sheets."""
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    try:
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()
        
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get("values", [])
        
        if not values:
            st.error("No data found.")
            return None
        else:
            headers = values[0]
            data = values[1:]
            df = pd.DataFrame(data, columns=headers)
            return df
    except HttpError as error:
        st.error(f"An error occurred: {error}")
        return None

def main():
    st.sidebar.title("Obesity Levels Visualization and Insights")
    options = st.sidebar.radio("Go to", ["About Dataset", "Data Preview", "Obesity Levels by Gender", "Overall Gender Distribution", "All Features by Gender","Line charts display trends", "Correlation Matrix", "Pivot Table"])

    df = get_sheet_data()
    
    if df is not None:
        # Convert columns to appropriate data types
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
        df['Height'] = pd.to_numeric(df['Height'], errors='coerce')
        df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')
        
        if 'Gender' in df.columns and 'NObeyesdad' in df.columns:
            df['Gender'] = df['Gender'].map({'0': 'Female', '1': 'Male'})

        if options == "About Dataset":
            st.title("About Dataset")
            st.write("""
            The original dataset was taken from [Kaggle](https://www.kaggle.com/datasets/fatemehmehrparvar/obesity-levels?resource=download).
            """)
            st.write("### Obesity")
            st.write("""
            Obesity, which causes physical and mental problems, is a global health problem with serious consequences. The prevalence of obesity is increasing steadily, and therefore, new research is needed that examines the influencing factors of obesity and how to predict the occurrence of the condition according to these factors.
            """)
            st.write("### Dataset Information")
            st.write("""
            This dataset includes data for the estimation of obesity levels in individuals from the countries of Mexico, Peru, and Colombia, based on their eating habits and physical condition. The data contains 17 attributes and 2111 records. The records are labeled with the class variable NObeyesdad (Obesity Level), which allows classification of the data using the values of Insufficient Weight, Normal Weight, Overweight Level I, Overweight Level II, Obesity Type I, Obesity Type II, and Obesity Type III. 77% of the data was generated synthetically using the Weka tool and the SMOTE filter, while 23% of the data was collected directly from users through a web platform.
            """)
            st.write("### Features:")
            st.write("""
            - Gender: Feature, Categorical, "Gender"
            - Age: Feature, Continuous, "Age"
            - Height: Feature, Continuous
            - Weight: Feature, Continuous
            - family_history_with_overweight: Feature, Binary, "Has a family member suffered or suffers from overweight?"
            - FAVC: Feature, Binary, "Do you eat high caloric food frequently?"
            - FCVC: Feature, Integer, "Do you usually eat vegetables in your meals?"
            - NCP: Feature, Continuous, "How many main meals do you have daily?"
            - CAEC: Feature, Categorical, "Do you eat any food between meals?"
            - SMOKE: Feature, Binary, "Do you smoke?"
            - CH2O: Feature, Continuous, "How much water do you drink daily?"
            - SCC: Feature, Binary, "Do you monitor the calories you eat daily?"
            - FAF: Feature, Continuous, "How often do you have physical activity?"
            - TUE: Feature, Integer, "How much time do you use technological devices such as cell phone, videogames, television, computer, and others?"
            - CALC: Feature, Categorical, "How often do you drink alcohol?"
            - MTRANS: Feature, Categorical, "Which transportation do you usually use?"
            - NObeyesdad: Target, Categorical, "Obesity level"
            """)

        if options == "Data Preview":
            st.title("Data Preview")
            st.dataframe(df)
            buffer = io.StringIO()
            df.info(buf=buffer)
            s = buffer.getvalue()
            st.text(s)
            st.dataframe(df.describe())
            st.write("### Discussion:")
            st.write("After preprocessing the raw data, including melting the dataset into a suitable format for visualization, all the visualizations presented herein were derived. These visualizations offer valuable insights into various aspects of the dataset, such as obesity levels by gender, overall gender distribution, feature values categorized by gender, and relationships between different variables. Each visualization serves to illuminate different facets of the data, aiding in better understanding and interpretation of the underlying trends and patterns.")

        if options == "Obesity Levels by Gender":
            st.title("Obesity Levels by Gender")
            obesity_gender_counts = df[df['NObeyesdad'].astype(float) <= 3]['Gender'].value_counts()
            fig1 = px.pie(obesity_gender_counts, names=obesity_gender_counts.index, values=obesity_gender_counts.values, title='Obesity Levels by Gender')
            st.plotly_chart(fig1)
            st.write("### Insights")
            st.write("The slight predominance of males might indicate a higher prevalence or risk of obesity among males within the specified range. This could be due to a variety of factors including lifestyle, dietary habits, or genetic predispositions that warrant further investigation. Given that nearly half of the individuals with obesity (in the specified range) are female, health interventions and policies should be equally targeted towards both genders to effectively address and manage obesity-related health issues.")

        if options == "Overall Gender Distribution":
            st.title("Overall Gender Distribution")
            gender_counts = df['Gender'].value_counts()
            fig2 = px.pie(gender_counts, names=gender_counts.index, values=gender_counts.values, title='Overall Gender Distribution')
            st.plotly_chart(fig2)
            st.write("### Insights")
            st.write("Despite the slight predominance of males, suggesting a potentially higher prevalence or risk of obesity within this range, it's crucial to acknowledge that nearly half of individuals with obesity fall within the female category. This distribution underscores the importance of gender-neutral health interventions and policies to effectively address and manage obesity-related health issues.")

        if options == "All Features by Gender":
            st.title("Feature Values by Gender")
            melted_df = df.melt(id_vars='Gender', value_vars=df.columns[1:], var_name='Feature', value_name='Value')
            fig3 = px.bar(melted_df, x='Feature', y='Value', color='Gender', barmode='group', title='Feature Values by Gender')
            st.plotly_chart(fig3)
            st.write("### Insights")
            st.write("The bar chart above displays the distribution of feature values categorized by gender. By examining this visualization, we can derive several insights:")
            st.write("1. **Gender Disparities**: Across various features, differences in values between genders are observable. For instance, there may be variations in the frequency of high-caloric food consumption, vegetable intake, or physical activity levels between males and females.")
            st.write("2. **Feature Importance**: Certain features may exhibit more pronounced differences between genders, indicating their potential importance in predicting obesity levels. Identifying these influential features can aid in refining predictive models and designing targeted interventions.")
            st.write("3. **Potential Trends**: Trends or patterns in feature values across gender groups may emerge, providing valuable insights into the behavioral or lifestyle factors associated with obesity. These trends can inform targeted strategies for obesity prevention and management tailored to specific gender demographics.")

        if options == "Line charts display trends":
            st.title("Line charts display trends")
            st.write("In the line chart depicting the distribution of obesity levels by gender, there is a noticeable trend where males consistently have higher counts across most obesity categories compared to females. This slight difference indicates that obesity is more prevalent among males in the dataset, suggesting potential underlying factors such as lifestyle, dietary habits, or genetic predispositions that may contribute to this disparity. These insights underscore the need for gender-specific strategies in addressing obesity-related health issues.")
        
            # Calculate counts of each obesity level for each gender
            obesity_counts = df.groupby(['NObeyesdad', 'Gender']).size().reset_index(name='Counts')
            obesity_counts['NObeyesdad'] = obesity_counts['NObeyesdad'].map({
                '0': 'Insufficient Weight',
                '1': 'Normal Weight',
                '2': 'Obesity Type I',
                '3': 'Obesity Type II',
                '4': 'Obesity Type III',
                '5': 'Overweight Level I',
                '6': 'Overweight Level II'
            })

            # Create line chart
            fig_line_chart = px.line(obesity_counts, x='NObeyesdad', y='Counts', color='Gender', title='Distribution of Obesity Levels by Gender')
            st.plotly_chart(fig_line_chart)

        if options == "Correlation Matrix":
            st.title("Correlation Matrix Heatmap")
            numeric_df = df[['Age', 'Height', 'Weight', 'CALC', 'FAVC', 'FCVC', 'NCP', 'SCC', 'SMOKE', 'CH2O', 'family_history_with_overweight', 'FAF', 'TUE', 'CAEC', 'MTRANS']]
            corr = numeric_df.corr()
            fig6, ax6 = plt.subplots()
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax6)
            ax6.set_title('Correlation Matrix Heatmap')
            st.pyplot(fig6)
            st.write("### Color indications and Insights")
            st.write("In the correlation matrix heatmap, the color gradient transitions from blue, indicating low correlations among predictor variables, to red, signifying high collinearity. This visualization allows us to discern the strength and direction of relationships between variables, aiding in the identification of potential multicollinearity issues within the dataset.")
            st.write("In analyzing the correlation matrix heatmap, we observe a gradient from blue to red, denoting varying degrees of correlation among predictor variables. However, the absence of intense red hues suggests no instances of high collinearity within these variables. This conclusion is indicative of a lack of overfitting to our features, reassuring the robustness of our model against multicollinearity issues.")

        if options == "Pivot Table":
            st.title("Pivot Table")
            st.write("Summarized patient information to give a detailed overview of patient number of count and mean average of ages.")
            
            # Create a pivot table. Adjust these column names based on your actual dataset.
            pivot_table = pd.pivot_table(df, 
                                         values=['Age'], # Add other metrics like costs, days admitted if available
                                         index=['Gender'], 
                                         aggfunc={'Age': ['mean', 'count']}) # Add other aggregation functions if needed
            
            st.write(pivot_table)

if __name__ == "__main__":
    main()
