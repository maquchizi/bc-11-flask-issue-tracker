from util import query_db


def get_all_issues():
    '''
        Called when super admin logs in
        Get all issues on the system
    '''
    response = query_db('''SELECT istbl.issue_id,istbl.raised_by,
            istbl.description,istbl.created,usrtbl.forename AS raised_forename,
            usrtbl.surname AS raised_surname,
            usrtbl2.forename AS assigned_to_forename,
            usrtbl2.surname AS assigned_to_surname,isstbl.status_name
            FROM issues AS istbl INNER JOIN users AS usrtbl ON
            istbl.raised_by = usrtbl.user_id
            LEFT JOIN users AS usrtbl2 ON
            istbl.assigned_to = usrtbl2.user_id
            INNER JOIN issue_status AS isstbl ON
            istbl.status = isstbl.issue_status_id
        ORDER BY istbl.created desc''')
    return response if response else False


def get_department_issues(user_id):
    '''
        Called when a department admin logs in
        Get all issues tagged for their department
    '''
    department_id = is_department_admin(user_id)
    if department_id:
        response = query_db('''SELECT istbl.issue_id,istbl.raised_by,
            istbl.description,istbl.created,usrtbl.forename AS raised_forename,
            usrtbl.surname AS raised_surname,
            usrtbl2.forename AS assigned_to_forename,
            usrtbl2.surname AS assigned_to_surname,isstbl.status_name
            FROM issues AS istbl INNER JOIN users AS usrtbl ON
            istbl.raised_by = usrtbl.user_id
            LEFT JOIN users AS usrtbl2 ON
            istbl.assigned_to = usrtbl2.user_id
            INNER JOIN issue_status AS isstbl ON
            istbl.status = isstbl.issue_status_id
            WHERE department = ? ORDER BY istbl.created desc''',
                            [department_id])
        return response if response else False
    else:
        return False


def get_my_issues(client_id):
    '''
        Called when a client logs in
        Get all issues client raised
    '''
    response = query_db('''SELECT istbl.issue_id,istbl.raised_by,
            istbl.description,istbl.created,usrtbl.forename AS raised_forename,
            usrtbl.surname AS raised_surname,
            usrtbl2.forename AS assigned_to_forename,
            usrtbl2.surname AS assigned_to_surname,isstbl.status_name
            FROM issues AS istbl INNER JOIN users AS usrtbl ON
            istbl.raised_by = usrtbl.user_id
            LEFT JOIN users AS usrtbl2 ON
            istbl.assigned_to = usrtbl2.user_id
            INNER JOIN issue_status AS isstbl ON
            istbl.status = isstbl.issue_status_id
            WHERE raised_by = ?
            ORDER BY istbl.created desc''',
                        [client_id])
    return response if response else False


def get_assigned_issues(rep_id):
    '''
        Called when a support rep logs in
        Get all issues asisgned to rep
    '''
    response = query_db('''SELECT istbl.issue_id,istbl.raised_by,
            istbl.description,istbl.created,usrtbl.forename AS raised_forename,
            usrtbl.surname AS raised_surname,
            usrtbl2.forename AS assigned_to_forename,
            usrtbl2.surname AS assigned_to_surname,isstbl.status_name
            FROM issues AS istbl INNER JOIN users AS usrtbl ON
            istbl.raised_by = usrtbl.user_id
            LEFT JOIN users AS usrtbl2 ON
            istbl.assigned_to = usrtbl2.user_id
            INNER JOIN issue_status AS isstbl ON
            istbl.status = isstbl.issue_status_id
            WHERE assigned_to = ?
            ORDER BY istbl.created desc''',
                        [rep_id])
    return response if response else False


def is_department_admin(user_id):
    '''
        Check if a user is a department admin
        If they are, return the department_id
    '''
    response = query_db('''SELECT department_id FROM departments
                        WHERE department_admin = ?''',
                        [user_id], one=True)
    return response[0] if response else False


def get_department_admin(department_id):
    '''
        Get the user_id of a department admin given the deparment_id
    '''
    response = query_db('''SELECT department_admin FROM departments
                        WHERE department_id = ?''',
                        [department_id], one=True)
    return response[0] if response else False
