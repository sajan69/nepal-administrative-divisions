#Copyright (c) 2024 Sajan Adhikari. All rights reserved.
from flask import Flask, jsonify, render_template, request
from flask_restx import Api, Resource, fields
import json
from decouple import config

app = Flask(__name__)
api = Api(app, version='1.0', title='Nepal Administrative Divisions API',
    description='A simple API for Nepal\'s administrative divisions',
    doc='/docs', prefix='/api')


# Load the combined data from environment variable
combined_data = json.loads(config('NEPAL_ADMIN_DATA'))

# Define namespaces
ns_provinces = api.namespace('provinces', description='Province operations')
ns_districts = api.namespace('districts', description='District operations')
ns_municipalities = api.namespace('municipalities', description='Municipality operations')

# Define models
province_model = api.model('Province', {
    'name': fields.String(required=True, description='Province name')
})

district_model = api.model('District', {
    'name': fields.String(required=True, description='District name'),
    'province': fields.String(required=True, description='Province name')
})

municipality_model = api.model('Municipality', {
    'name': fields.String(required=True, description='Municipality name'),
    'district': fields.String(required=True, description='District name'),
    'province': fields.String(required=True, description='Province name')
})

@app.route('/')
def home():
    try:
        return render_template('index.html', provinces=combined_data['provinces'].keys())
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@ns_provinces.route('/')
class ProvinceList(Resource):
    @api.doc('list_provinces')
    def get(self):
        """List all provinces"""
        return list(combined_data['provinces'].keys())

@ns_districts.route('/')
class DistrictList(Resource):
    @api.doc('list_districts')
    @api.param('province', 'The province name', _in='query')
    def get(self):
        """List all districts in a province"""
        province = request.args.get('province')
        if not province:
            return list(set(district for prov in combined_data['provinces'].values() 
                            for district in prov['districts'].keys()))
        if province in combined_data['provinces']:
            return list(combined_data['provinces'][province]['districts'].keys())
        api.abort(404, f"Province {province} not found")

@ns_municipalities.route('/')
class MunicipalityList(Resource):
    @api.doc('list_municipalities')
    @api.param('province', 'The province name', _in='query')
    @api.param('district', 'The district name', _in='query')
    def get(self):
        """List all municipalities in a district"""
        province = request.args.get('province')
        district = request.args.get('district')
        if not province and not district:
            return list(set(muni for prov in combined_data['provinces'].values() 
                            for dist in prov['districts'].values() 
                            for muni in dist['municipalities']))
        if province and not district:
            return list(set(muni for dist in combined_data['provinces'][province]['districts'].values() 
                            for muni in dist['municipalities']))
        if province in combined_data['provinces'] and district in combined_data['provinces'][province]['districts']:
            return combined_data['provinces'][province]['districts'][district]['municipalities']
        api.abort(404, f"Province {province} or district {district} not found")

# Keep the existing routes
@app.route('/province/<province>')
def province_page(province):
    if province in combined_data['provinces']:
        districts = combined_data['provinces'][province]['districts'].keys()
        return render_template('province.html', province=province, districts=districts)
    return "Province not found", 404

@app.route('/district/<province>/<district>')
def district_page(province, district):
    if province in combined_data['provinces'] and district in combined_data['provinces'][province]['districts']:
        municipalities = combined_data['provinces'][province]['districts'][district]['municipalities']
        return render_template('district.html', province=province, district=district, municipalities=municipalities)
    return "District not found", 404

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = {}
    all_data = {'provinces': combined_data['provinces']}

    if query:
        for province, province_data in combined_data['provinces'].items():
            province_lower = province.lower()
            if query in province_lower:
                results[province] = {
                    'type': 'province',
                    'districts': province_data['districts'],
                    'district_count': len(province_data['districts'])
                }
            for district, district_data in province_data['districts'].items():
                district_lower = district.lower()
                if query in district_lower:
                    results[district] = {
                        'type': 'district',
                        'province': province,
                        'municipalities': district_data['municipalities'],
                        'municipality_count': len(district_data['municipalities'])
                    }
                for municipality in district_data['municipalities']:
                    if query in municipality.lower():
                        results[municipality] = {
                            'type': 'municipality',
                            'district': district,
                            'province': province
                        }

    return render_template('search.html', query=query, results=results, all_data=all_data)

@app.route('/visualize')
def visualize():
    province_data = {province: len(data['districts']) for province, data in combined_data['provinces'].items()}
    all_data = {'provinces': combined_data['provinces']}
    return render_template('visualize.html', province_data=province_data, all_data=all_data)

if __name__ == '__main__':
    app.run(debug=True)

# Vercel entry point
app = app