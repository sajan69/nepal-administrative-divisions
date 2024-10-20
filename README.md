# Nepal Administrative Divisions

## Overview

This project provides a comprehensive web application and API for accessing and visualizing administrative divisions of Nepal. It includes information about provinces, districts, and municipalities, offering both a user-friendly web interface and a RESTful API for developers.

## Features

- Web interface for browsing Nepal's administrative divisions
- Interactive visualization of administrative data
- Search functionality for provinces, districts, and municipalities
- RESTful API for programmatic access to the data
- Swagger documentation for easy API exploration

## Technologies Used

- Flask: Web framework for Python
- Flask-RESTX: Extension for building REST APIs with Swagger documentation
- Chart.js: JavaScript library for data visualization
- HTML/CSS: Frontend structure and styling

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/sajan69/nepal-administrative-divisions.git
   cd nepal-administrative-divisions
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open a web browser and navigate to `http://localhost:5000`

## API Documentation

The API documentation is available at `/docs` when running the application. It provides a Swagger UI for easy exploration and testing of the API endpoints.

### API Endpoints

- `/api/provinces/`: List all provinces
- `/api/districts/`: List all districts or districts in a specific province
- `/api/municipalities/`: List all municipalities, municipalities in a province, or municipalities in a specific district

### Example API Usage

1. Get all provinces:
   ```
   GET /api/provinces/
   ```

2. Get districts in a specific province:
   ```
   GET /api/districts/?province=Bagmati
   ```

3. Get municipalities in a specific district:
   ```
   GET /api/municipalities/?province=Bagmati&district=Kathmandu
   ```

## Web Application Usage

1. Home Page: Displays a list of all provinces
2. Province Page: Shows districts within a selected province
3. District Page: Lists municipalities within a selected district
4. Search: Allows searching for any administrative division
5. Visualize: Provides interactive charts of administrative data

## Contributing

Contributions to this project are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



## Contact

For any queries or suggestions, please contact:
Sajan Adhikari
- GitHub: [@sajanadhikari](https://github.com/sajan69)
- LinkedIn: [Sajan Adhikari](https://www.linkedin.com/in/sajanadhikari)
- Twitter: [@sajanadhikari_](https://twitter.com/sajanadhikari_)
