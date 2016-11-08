from util import query_db


def get_all_issues():
    '''
        Called when super admin logs in
        Get all issues on the system
    '''
    response = query_db('''SELECT istbl.issue_id,istbl.raised_by,
        istbl.description,istbl.created,usrtbl.forename AS raised_forename,
        usrtbl.surname AS raised_surname
        FROM issues AS istbl INNER JOIN users AS usrtbl ON
        istbl.raised_by = usrtbl.user_id''')
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
            usrtbl.surname AS raised_surname
            FROM issues AS istbl INNER JOIN users AS usrtbl ON
            istbl.raised_by = usrtbl.user_id WHERE department = ?''',
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
            usrtbl.surname AS raised_surname
            FROM issues AS istbl INNER JOIN users AS usrtbl ON
            istbl.raised_by = usrtbl.user_id WHERE department = ?''',
                        [client_id])
    return response if response else False


def get_assigned_issues(rep_id):
    '''
        Called when a support rep logs in
        Get all issues asisgned to rep
    '''
    response = query_db('''SELECT * FROM issues WHERE assigned_to = ?''',
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
