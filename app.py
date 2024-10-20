from pprint import pformat
from flask import Flask, jsonify, render_template, request
from flask_restx import Api, Resource, fields
import json
import requests
from decouple import config
import os
app = Flask(__name__)
api = Api(app, version='1.0', title='Nepal Administrative Divisions API',
    description='A simple API for Nepal\'s administrative divisions',
    doc='/docs', prefix='/api')

# Load the combined data from environment variable
NEPAL_ADMIN_DATA_URL = config('NEPAL_ADMIN_DATA_URL')
response = requests.get(NEPAL_ADMIN_DATA_URL)
combined_data = response.json()
# Define namespaces
ns_provinces = api.namespace('provinces', description='Province operations')
ns_districts = api.namespace('districts', description='District operations')
ns_municipalities = api.namespace('municipalities', description='Municipality operations')

# Define models
province_model = api.model('Province', {
    'id': fields.Integer(required=True, description='Province ID'),
    'name': fields.String(required=True, description='Province name'),
    'area_sq_km': fields.String(required=True, description='Area in square kilometers'),
    'website': fields.String(required=True, description='Province website'),
    'headquarter': fields.String(required=True, description='Province headquarter')
})

district_model = api.model('District', {
    'id': fields.Integer(required=True, description='District ID'),
    'name': fields.String(required=True, description='District name'),
    'area_sq_km': fields.String(required=True, description='Area in square kilometers'),
    'website': fields.String(required=True, description='District website'),
    'headquarter': fields.String(required=True, description='District headquarter')
})

municipality_model = api.model('Municipality', {
    'id': fields.Integer(required=True, description='Municipality ID'),
    'category_id': fields.Integer(required=True, description='Category ID'),
    'name': fields.String(required=True, description='Municipality name'),
    'area_sq_km': fields.String(required=True, description='Area in square kilometers'),
    'website': fields.String(required=True, description='Municipality website'),
    'wards': fields.List(fields.Integer, required=True, description='List of wards')
})

@ns_provinces.route('/')
class ProvinceList(Resource):
    @api.doc('list_provinces')
    @api.marshal_list_with(province_model)
    def get(self):
        """List all provinces"""
        return combined_data
@ns_districts.route('/')
class DistrictList(Resource):
    @api.doc('list_districts')
    @api.param('province_id', 'The province ID', _in='query')
    @api.param('province_name', 'The province name', _in='query')
    @api.marshal_list_with(district_model)
    def get(self):
        """List all districts in a province"""
        province_id = request.args.get('province_id')
        province_name = request.args.get('province_name')
        
        if not province_id and not province_name:
            return [
                district
                for province in combined_data
                for district in (province['districts'].values() if isinstance(province['districts'], dict) else province['districts'])
            ]
        
        if province_id:
            province = next((p for p in combined_data if p['id'] == int(province_id)), None)
        elif province_name:
            province = next((p for p in combined_data if p['name'].lower() == province_name.lower()), None)
        else:
            province = None
        
        if province:
            return list(province['districts'].values()) if isinstance(province['districts'], dict) else province['districts']
        
        api.abort(404, f"Province not found")

@ns_municipalities.route('/')
class MunicipalityList(Resource):
    @api.doc('list_municipalities')
    @api.param('province_id', 'The province ID', _in='query')
    @api.param('province_name', 'The province name', _in='query')
    @api.param('district_id', 'The district ID', _in='query')
    @api.param('district_name', 'The district name', _in='query')
    @api.marshal_list_with(municipality_model)
    def get(self):
        """List all municipalities in a district"""
        province_id = request.args.get('province_id')
        province_name = request.args.get('province_name')
        district_id = request.args.get('district_id')
        district_name = request.args.get('district_name')
        
        if not any([province_id, province_name, district_id, district_name]):
            return [
                municipality
                for province in combined_data
                for district in (province['districts'].values() if isinstance(province['districts'], dict) else province['districts'])
                for municipality in (district['municipalities'].values() if isinstance(district['municipalities'], dict) else district['municipalities'])
            ]
        
        if province_id or province_name:
            if province_id:
                province = next((p for p in combined_data if p['id'] == int(province_id)), None)
            else:
                province = next((p for p in combined_data if p['name'].lower() == province_name.lower()), None)
            
            if not province:
                api.abort(404, f"Province not found")
            
            if not district_id and not district_name:
                return [
                    municipality
                    for district in (province['districts'].values() if isinstance(province['districts'], dict) else province['districts'])
                    for municipality in (district['municipalities'].values() if isinstance(district['municipalities'], dict) else district['municipalities'])
                ]
            
            districts = province['districts'].values() if isinstance(province['districts'], dict) else province['districts']
            
            if district_id:
                district = next((d for d in districts if d['id'] == int(district_id)), None)
            else:
                district = next((d for d in districts if d['name'].lower() == district_name.lower()), None)
            
            if district:
                return list(district['municipalities'].values()) if isinstance(district['municipalities'], dict) else district['municipalities']
        
        api.abort(404, f"District not found")

@app.route('/')
def home():
    try:
        provinces = combined_data
        return render_template('index.html', provinces=provinces)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.template_filter('pprint')
def pprint_filter(object):
    return pformat(object)

@app.route('/province/<int:province_id>')
def province_page(province_id):
    province = next((p for p in combined_data if p['id'] == province_id), None)
    if province:
        return render_template('province.html', province=province)
    return "Province not found", 404

@app.route('/district/<int:province_id>/<int:district_id>')
def district_page(province_id, district_id):
    province = next((p for p in combined_data if p['id'] == province_id), None)
    if province:
        districts = province['districts']
        if isinstance(districts, dict):
            district = districts.get(str(district_id))
        else:
            district = next((d for d in districts if d['id'] == district_id), None)
        if district:
            return render_template('district.html', province=province, district=district)
    return "District not found", 404

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = {}

    if query:
        for province in combined_data:
            if query in province['name'].lower():
                districts = province['districts'].values() if isinstance(province['districts'], dict) else province['districts']
                results[province['name']] = {
                    'type': 'province',
                    'id': province['id'],
                    'area_sq_km': province['area_sq_km'],
                    'website': province['website'],
                    'headquarter': province['headquarter'],
                    'district_count': len(districts),
                    'districts': districts
                }
            
            districts = province['districts'].values() if isinstance(province['districts'], dict) else province['districts']
            
            for district in districts:
                if query in district['name'].lower():
                    municipalities = district['municipalities'].values() if isinstance(district['municipalities'], dict) else district['municipalities']
                    results[district['name']] = {
                        'type': 'district',
                        'id': district['id'],
                        'province': province['name'],
                        'area_sq_km': district['area_sq_km'],
                        'website': district['website'],
                        'headquarter': district['headquarter'],
                        'municipality_count': len(municipalities),
                        'municipalities': municipalities
                    }
                
                municipalities = district['municipalities'].values() if isinstance(district['municipalities'], dict) else district['municipalities']
                
                for municipality in municipalities:
                    if query in municipality['name'].lower():
                        results[municipality['name']] = {
                            'type': 'municipality',
                            'id': municipality['id'],
                            'district': district['name'],
                            'province': province['name'],
                            'area_sq_km': municipality['area_sq_km'],
                            'website': municipality['website'],
                            'wards': municipality['wards']
                        }

    return render_template('search.html', query=query, results=results, combined_data=combined_data)

@app.route('/visualize')
def visualize():
    province_data = {province['name']: len(province['districts']) for province in combined_data}
    return render_template('visualize.html', province_data=province_data, combined_data=combined_data)

if __name__ == '__main__':
    app.run(debug=True)

# Vercel entry point
app = app