import logging
from flask import Blueprint, request, jsonify
from db import get_db, row_to_dict

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
def home():
    return jsonify({
        'message': 'Welcome to User Management API',
        'endpoints': {
            'GET /api/users': 'List users (supports page, limit, search, sort)',
            'POST /api/users': 'Create a new user',
            'GET /api/users/<id>': 'Get user by ID',
            'PUT /api/users/<id>': 'Update user (full)',
            'PATCH /api/users/<id>': 'Update user (partial)',
            'DELETE /api/users/<id>': 'Delete user',
            'GET /api/users/summary': 'User statistics'
        }
    }), 200


@users_bp.route('/api/users', methods=['GET'])
def get_users():
    logger.info("GET /api/users called")

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 5, type=int)
    search = request.args.get('search', '', type=str)
    sort = request.args.get('sort', '', type=str)

    conn = get_db()
    cursor = conn.cursor()

    query = 'SELECT * FROM users'
    params = []

    if search:
        query += ' WHERE (LOWER(first_name) LIKE ? OR LOWER(last_name) LIKE ?)'
        search_term = f'%{search.lower()}%'
        params.extend([search_term, search_term])
        logger.debug(f"Search filter applied: {search}")

    allowed_sort_fields = ['id', 'first_name', 'last_name', 'company_name',
                           'age', 'city', 'state', 'zip', 'email', 'web']
    if sort:
        if sort.startswith('-'):
            sort_field = sort[1:]
            sort_order = 'DESC'
        else:
            sort_field = sort
            sort_order = 'ASC'

        if sort_field in allowed_sort_fields:
            query += f' ORDER BY {sort_field} {sort_order}'
            logger.debug(f"Sorting by {sort_field} {sort_order}")
        else:
            logger.warning(f"Invalid sort field: {sort_field}")

    count_query = query.replace('SELECT *', 'SELECT COUNT(*)', 1)
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    offset = (page - 1) * limit
    query += ' LIMIT ? OFFSET ?'
    params.extend([limit, offset])

    cursor.execute(query, params)
    users = [row_to_dict(row) for row in cursor.fetchall()]
    conn.close()

    logger.info(f"Returning {len(users)} users (page {page})")

    return jsonify({
        'page': page,
        'limit': limit,
        'total': total,
        'users': users
    }), 200


@users_bp.route('/api/users', methods=['POST'])
def create_user():
    logger.info("POST /api/users called")
    data = request.get_json()

    if not data or not data.get('first_name') or not data.get('last_name'):
        logger.warning("Missing required fields: first_name and last_name")
        return jsonify({'error': 'first_name and last_name are required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (first_name, last_name, company_name, age,
                           city, state, zip, email, web)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('first_name'), data.get('last_name'), data.get('company_name'),
        data.get('age'), data.get('city'), data.get('state'), data.get('zip'),
        data.get('email'), data.get('web')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    logger.info(f"User created with id={new_id}")
    return jsonify({'message': 'User created', 'id': new_id}), 201


@users_bp.route('/api/users/summary', methods=['GET'])
def get_users_summary():
    logger.info("GET /api/users/summary called")
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    cursor.execute('SELECT AVG(age) FROM users')
    avg_age = cursor.fetchone()[0]
    avg_age = round(avg_age, 2) if avg_age else 0

    cursor.execute('''
        SELECT city, COUNT(*) as count
        FROM users GROUP BY city ORDER BY count DESC
    ''')
    cities = [{'city': row['city'], 'count': row['count']} for row in cursor.fetchall()]

    conn.close()

    logger.info("Summary generated successfully")
    return jsonify({
        'total_users': total_users,
        'average_age': avg_age,
        'count_by_city': cities
    }), 200


@users_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    logger.info(f"GET /api/users/{user_id} called")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        logger.warning(f"User with id={user_id} not found")
        return jsonify({'error': 'User not found'}), 404

    logger.info(f"Returning user id={user_id}")
    return jsonify(row_to_dict(user)), 200


@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    logger.info(f"PUT /api/users/{user_id} called")
    data = request.get_json()

    if not data or not data.get('first_name') or not data.get('last_name'):
        logger.warning("Missing required fields for PUT")
        return jsonify({'error': 'first_name and last_name are required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    if cursor.fetchone() is None:
        conn.close()
        logger.warning(f"User with id={user_id} not found for update")
        return jsonify({'error': 'User not found'}), 404

    cursor.execute('''
        UPDATE users
        SET first_name = ?, last_name = ?, company_name = ?, age = ?,
            city = ?, state = ?, zip = ?, email = ?, web = ?
        WHERE id = ?
    ''', (
        data.get('first_name'), data.get('last_name'), data.get('company_name'),
        data.get('age'), data.get('city'), data.get('state'), data.get('zip'),
        data.get('email'), data.get('web'), user_id
    ))
    conn.commit()
    conn.close()

    logger.info(f"User id={user_id} fully updated")
    return jsonify({'message': 'User updated'}), 200


@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    logger.info(f"DELETE /api/users/{user_id} called")
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    if cursor.fetchone() is None:
        conn.close()
        logger.warning(f"User with id={user_id} not found for deletion")
        return jsonify({'error': 'User not found'}), 404

    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    logger.info(f"User id={user_id} deleted")
    return jsonify({'message': 'User deleted'}), 200


@users_bp.route('/api/users/<int:user_id>', methods=['PATCH'])
def patch_user(user_id):
    logger.info(f"PATCH /api/users/{user_id} called")
    data = request.get_json()

    if not data:
        logger.warning("No data provided for PATCH")
        return jsonify({'error': 'No data provided'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    if cursor.fetchone() is None:
        conn.close()
        logger.warning(f"User with id={user_id} not found for patch")
        return jsonify({'error': 'User not found'}), 404

    allowed_fields = ['first_name', 'last_name', 'company_name', 'age',
                      'city', 'state', 'zip', 'email', 'web']
    fields_to_update = []
    values = []

    for field in allowed_fields:
        if field in data:
            fields_to_update.append(f'{field} = ?')
            values.append(data[field])

    if not fields_to_update:
        conn.close()
        logger.warning("No valid fields provided for PATCH")
        return jsonify({'error': 'No valid fields to update'}), 400

    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields_to_update)} WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

    logger.info(f"User id={user_id} partially updated: {list(data.keys())}")
    return jsonify({'message': 'User partially updated'}), 200
