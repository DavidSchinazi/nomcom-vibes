#!/usr/bin/env python3
import argparse
import requests
import json
import os
import random
from positions import get_nomcom_id, get_position_name, get_position_short_name

NOMINEES_DATA = None
NOMINEE_POSITIONS_DATA = None
ACTIVE_NOMINEES_DATA = None
NOMINEES_BY_POSITION_DATA = None
EMAILS_TO_PEOPLE_IDS = None
PERSON_IDS_DOWNLOADED = []
REGISTRATIONS_DOWNLOADED = []
GROUP_IDS_DOWNLOADED = []
MEETING_IDS_DOWNLOADED = []
SESSION_IDS_DOWNLOADED = []
MEETINGS_ATTENDED_DOWNLOADED = []
NOMINEE_IDS_DOWNLOADED = []
NOMCOM_GROUP_INFO_DATA = None
NOMCOM_PERSON_IDS = None


def load_nominees(force_metadata=False):
    global NOMINEES_DATA
    if NOMINEES_DATA:
        return NOMINEES_DATA

    nominees_file = "data/nominees.json"
    if not force_metadata and os.path.exists(nominees_file):
        with open(nominees_file, "r", encoding="utf-8") as f:
            NOMINEES_DATA = json.load(f)['objects']
            return NOMINEES_DATA

    nomcom_id = get_nomcom_id()
    url = f"https://datatracker.ietf.org/api/v1/nomcom/nominee/?nomcom={nomcom_id}&limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    nominees_data = response.json()

    os.makedirs(os.path.dirname(nominees_file), exist_ok=True)
    with open(nominees_file, "w", encoding="utf-8") as f:
        json.dump(nominees_data, f, indent=4)
    print(f"Nominees data downloaded and saved to {nominees_file}")
    NOMINEES_DATA = nominees_data['objects']
    return NOMINEES_DATA

def get_person_id_from_email(email, force_metadata=False):
    global EMAILS_TO_PEOPLE_IDS
    emails_file = "data/emails.json"
    if not EMAILS_TO_PEOPLE_IDS:
        EMAILS_TO_PEOPLE_IDS = {}
        if not force_metadata and os.path.exists(emails_file):
            with open(emails_file, "r", encoding="utf-8") as f:
                EMAILS_TO_PEOPLE_IDS = json.load(f)
    if email in EMAILS_TO_PEOPLE_IDS:
        return EMAILS_TO_PEOPLE_IDS[email]

    url = f'https://datatracker.ietf.org/api/v1/person/email/{email}/'
    response = requests.get(url)
    response.raise_for_status()
    email_data = response.json()
    person_path = email_data['person']
    person_id = person_path.strip('/').split('/')[-1]
    EMAILS_TO_PEOPLE_IDS[email] = person_id
    os.makedirs(os.path.dirname(emails_file), exist_ok=True)
    with open(emails_file, "w", encoding="utf-8") as f:
        json.dump(EMAILS_TO_PEOPLE_IDS, f, indent=4)
    return person_id

def get_person_info_from_id(person_id, force_metadata=False):
    global PERSON_IDS_DOWNLOADED
    person_file = f"data/persons/{person_id}.json"

    if os.path.exists(person_file) and ((not force_metadata) or (person_id in PERSON_IDS_DOWNLOADED)):
        with open(person_file, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f'https://datatracker.ietf.org/api/v1/person/person/{person_id}/'
    response = requests.get(url)
    response.raise_for_status()
    person_data = response.json()

    os.makedirs(os.path.dirname(person_file), exist_ok=True)
    with open(person_file, "w", encoding="utf-8") as f:
        json.dump(person_data, f, indent=4)
    print(f"Person data downloaded and saved to {person_file}")
    PERSON_IDS_DOWNLOADED.append(person_id)

    return person_data


def get_registrations_from_person_id(person_id, force_metadata=False):
    global REGISTRATIONS_DOWNLOADED
    registration_file = f"data/registrations/{person_id}.json"

    if os.path.exists(registration_file) and ((not force_metadata) or (person_id in REGISTRATIONS_DOWNLOADED)):
        with open(registration_file, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f'https://datatracker.ietf.org/api/v1/meeting/registration/?person={person_id}&limit=1000'
    response = requests.get(url)
    response.raise_for_status()
    registration_data = response.json()

    os.makedirs(os.path.dirname(registration_file), exist_ok=True)
    with open(registration_file, "w", encoding="utf-8") as f:
        json.dump(registration_data, f, indent=4)
    print(f"Registration data downloaded and saved to {registration_file}")
    REGISTRATIONS_DOWNLOADED.append(person_id)

    return registration_data


def get_group_info_from_id(group_id, force_metadata=False):
    global GROUP_IDS_DOWNLOADED
    group_file = f"data/groups/{group_id}.json"

    if os.path.exists(group_file) and ((not force_metadata) or (group_id in GROUP_IDS_DOWNLOADED)):
        with open(group_file, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f'https://datatracker.ietf.org/api/v1/group/group/{group_id}/'
    response = requests.get(url)
    response.raise_for_status()
    group_data = response.json()

    os.makedirs(os.path.dirname(group_file), exist_ok=True)
    with open(group_file, "w", encoding="utf-8") as f:
        json.dump(group_data, f, indent=4)
    print(f"Group data downloaded and saved to {group_file}")
    GROUP_IDS_DOWNLOADED.append(group_id)

    return group_data


def get_meeting_info_from_id(meeting_id, force_metadata=False):
    global MEETING_IDS_DOWNLOADED
    meeting_file = f"data/meetings/{meeting_id}.json"

    if os.path.exists(meeting_file) and ((not force_metadata) or (meeting_id in MEETING_IDS_DOWNLOADED)):
        with open(meeting_file, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f'https://datatracker.ietf.org/api/v1/meeting/meeting/{meeting_id}/'
    response = requests.get(url)
    response.raise_for_status()
    meeting_data = response.json()

    os.makedirs(os.path.dirname(meeting_file), exist_ok=True)
    with open(meeting_file, "w", encoding="utf-8") as f:
        json.dump(meeting_data, f, indent=4)
    print(f"Meeting data downloaded and saved to {meeting_file}")
    MEETING_IDS_DOWNLOADED.append(meeting_id)

    return meeting_data


def get_session_info_from_id(session_id, force_metadata=False):
    global SESSION_IDS_DOWNLOADED
    session_file = f"data/sessions/{session_id}.json"

    if os.path.exists(session_file) and ((not force_metadata) or (session_id in SESSION_IDS_DOWNLOADED)):
        with open(session_file, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f'https://datatracker.ietf.org/api/v1/meeting/session/{session_id}/'
    response = requests.get(url)
    response.raise_for_status()
    session_data = response.json()

    os.makedirs(os.path.dirname(session_file), exist_ok=True)
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=4)
    print(f"Session data downloaded and saved to {session_file}")
    SESSION_IDS_DOWNLOADED.append(session_id)

    return session_data


def get_meetings_attended_from_person_id(person_id, force_metadata=False):
    global MEETINGS_ATTENDED_DOWNLOADED
    meetings_attended_file = f"data/meetings_attended/{person_id}.json"

    if os.path.exists(meetings_attended_file) and ((not force_metadata) or (person_id in MEETINGS_ATTENDED_DOWNLOADED)):
        with open(meetings_attended_file, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f'https://datatracker.ietf.org/api/v1/meeting/attended/?person={person_id}&limit=1000'
    response = requests.get(url)
    response.raise_for_status()
    meetings_attended_data = response.json()

    os.makedirs(os.path.dirname(meetings_attended_file), exist_ok=True)
    with open(meetings_attended_file, "w", encoding="utf-8") as f:
        json.dump(meetings_attended_data, f, indent=4)
    print(f"Meetings attended data downloaded and saved to {meetings_attended_file}")
    MEETINGS_ATTENDED_DOWNLOADED.append(person_id)

    return meetings_attended_data


def get_person_info_from_email(email, force_metadata=False):
    return get_person_info_from_id(get_person_id_from_email(email, force_metadata=force_metadata), force_metadata=force_metadata)

def get_nominee_info(nominee_id, force_metadata=False):
    global NOMINEE_IDS_DOWNLOADED
    nominee_file = f"data/nominees/{nominee_id}.json"
    if os.path.exists(nominee_file) and ((not force_metadata) or (nominee_id in NOMINEE_IDS_DOWNLOADED)):
        with open(nominee_file, "r", encoding="utf-8") as f:
            return json.load(f)

    nominee = None
    for obj in load_nominees(force_metadata=force_metadata):
        if str(obj['id']) == str(nominee_id):
            nominee = obj
            break
    if not nominee:
        raise Exception(f'Nominee with id {nominee_id} not found')

    email_path = nominee['email']
    email = email_path.strip('/').split('/')[-1]
    person_id = get_person_id_from_email(email, force_metadata=force_metadata)
    nominee_info = get_person_info_from_id(person_id, force_metadata=force_metadata)

    url = f'https://datatracker.ietf.org/api/v1/meeting/registration/?person={nominee_info["id"]}&limit=1'
    response = requests.get(url)
    response.raise_for_status()
    attended_data = response.json()
    nominee_info['num_meetings_registered'] = attended_data['meta']['total_count']

    url = f'https://datatracker.ietf.org/api/v1/doc/documentauthor/?email={email}&limit=1000'
    response = requests.get(url)
    response.raise_for_status()
    drafts_data = response.json()
    num_individual_drafts = 0
    num_wg_drafts = 0
    num_rfcs = 0
    for document in drafts_data['objects']:
        document_path = document['document']
        if document_path.startswith('/api/v1/doc/document/rfc'):
            num_rfcs += 1
        elif document_path.startswith('/api/v1/doc/document/draft-ietf-'):
            num_wg_drafts += 1
        elif document_path.startswith('/api/v1/doc/document/draft-'):
            num_individual_drafts += 1
    nominee_info['num_documents'] = drafts_data['meta']['total_count']
    nominee_info['num_individual_drafts'] = num_individual_drafts
    nominee_info['num_wg_drafts'] = num_wg_drafts
    nominee_info['num_rfcs'] = num_rfcs

    nominee_info['nominee_id'] = nominee_id
    nominee_info['email'] = email
    nominee_positions_data = get_nominee_positions(force_metadata=force_metadata)
    positions = {}
    for r in nominee['nominee_position']:
        short_name = get_position_short_name(get_position_name(r, force_metadata=force_metadata))
        state = 'unknown'
        for np in nominee_positions_data:
            if np['nominee'] == nominee['resource_uri'] and np['position'] == r:
                state = np['state'].split('/')[-2]
                break
        positions[short_name] = state
    nominee_info['positions'] = positions

    os.makedirs(os.path.dirname(nominee_file), exist_ok=True)
    with open(nominee_file, "w", encoding="utf-8") as f:
        json.dump(nominee_info, f, indent=4)
    print(f"Nominee info downloaded and saved to {nominee_file}")
    NOMINEE_IDS_DOWNLOADED.append(nominee_id)

    return nominee_info

def print_info_from_email(email, force_metadata=False):
    person_id = get_person_id_from_email(email, force_metadata=force_metadata)
    meetings_attended = get_meetings_attended_from_person_id(person_id, force_metadata=force_metadata)
    registrations_data = get_registrations_from_person_id(person_id, force_metadata=force_metadata)

    meetings_data = {}
    for session in meetings_attended['objects']:
        session_id = session['session'].strip('/').split('/')[-1]
        session_info = get_session_info_from_id(session_id, force_metadata=force_metadata)

        meeting_id = session_info['meeting'].strip('/').split('/')[-1]
        group_id = session_info['group'].strip('/').split('/')[-1]

        meeting_info = get_meeting_info_from_id(meeting_id, force_metadata=force_metadata)
        group_info = get_group_info_from_id(group_id, force_metadata=force_metadata)

        meeting_number = meeting_info['number']
        meeting_date = meeting_info['date']
        if meeting_number not in meetings_data:
            meetings_data[meeting_number] = {'date': meeting_date, 'groups': set()}

        meetings_data[meeting_number]['groups'].add(group_info['acronym'])

    for registration in registrations_data['objects']:
        meeting_id = registration['meeting'].strip('/').split('/')[-1]
        meeting_info = get_meeting_info_from_id(meeting_id, force_metadata=force_metadata)
        meeting_number = meeting_info['number']
        meeting_date = meeting_info['date']
        if meeting_number not in meetings_data:
            meetings_data[meeting_number] = {'date': meeting_date, 'groups': set()}

    sorted_meetings = sorted(meetings_data.items(), key=lambda item: item[1]['date'])
    for meeting_number, details in sorted_meetings:
        group_str = ', '.join(sorted(list(details['groups'])))
        ietf_str = 'IETF ' if meeting_number.isdigit() else ''
        print(f"{ietf_str}{meeting_number}: {group_str}")


def print_nominee_info(force_metadata=False):
    """Prints each nominee and the number of IETF meetings they have attended, sorted in descending order."""
    nominees_data = get_active_nominees(force_metadata=force_metadata)
    nominee_stats = []
    for nominee in nominees_data:
        nominee_info = get_nominee_info(nominee['id'], force_metadata=force_metadata)
        name = nominee_info['name']
        meetings_registered = nominee_info['num_meetings_registered']
        num_documents = nominee_info['num_documents']
        nominee_stats.append({'name': name, 'meetings': meetings_registered, 'documents': num_documents})

    nominee_stats.sort(key=lambda x: x['meetings'] + x['documents'], reverse=True)
    max_name_len = max(len(item['name']) for item in nominee_stats)
    for item in nominee_stats:
        print(f"{item['name']:>{max_name_len}}: {item['meetings']:>3} meetings, {item['documents']:>3} documents")
    print("We have a total of {} nominees.".format(len(nominees_data)))

def get_nominee_positions(force_metadata=False):
    global NOMINEE_POSITIONS_DATA
    if NOMINEE_POSITIONS_DATA:
        return NOMINEE_POSITIONS_DATA

    nominee_positions_file = "data/nominee_positions.json"
    if not force_metadata and os.path.exists(nominee_positions_file):
        with open(nominee_positions_file, "r", encoding="utf-8") as f:
            NOMINEE_POSITIONS_DATA = json.load(f)['objects']
            return NOMINEE_POSITIONS_DATA

    url = "https://datatracker.ietf.org/api/v1/nomcom/nomineeposition/?limit=4000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    nominee_positions_data = response.json()

    os.makedirs(os.path.dirname(nominee_positions_file), exist_ok=True)
    with open(nominee_positions_file, "w", encoding="utf-8") as f:
        json.dump(nominee_positions_data, f, indent=4)
    print(f"Nominee positions data downloaded and saved to {nominee_positions_file}")
    NOMINEE_POSITIONS_DATA = nominee_positions_data['objects']
    return NOMINEE_POSITIONS_DATA

NOMCOM_GROUP_ID = None
def get_nomcom_group_id(force_metadata=False):
    global NOMCOM_GROUP_ID
    if NOMCOM_GROUP_ID:
        return NOMCOM_GROUP_ID

    nomcom_id = get_nomcom_id()
    nomcom_group_file = f"data/nomcom_id.json"
    if not force_metadata and os.path.exists(nomcom_group_file):
        with open(nomcom_group_file, "r", encoding="utf-8") as f:
            NOMCOM_GROUP_ID = json.load(f)['group'].strip('/').split('/')[-1]
            return NOMCOM_GROUP_ID

    url = f"https://datatracker.ietf.org/api/v1/nomcom/nomcom/{nomcom_id}/"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    nomcom_data = response.json()

    os.makedirs(os.path.dirname(nomcom_group_file), exist_ok=True)
    with open(nomcom_group_file, "w", encoding="utf-8") as f:
        json.dump(nomcom_data, f, indent=4)
    print(f"Nomcom group data downloaded and saved to {nomcom_group_file}")
    NOMCOM_GROUP_ID = nomcom_data['group'].strip('/').split('/')[-1]
    return NOMCOM_GROUP_ID


def get_nomcom_group_info(force_metadata=False):
    global NOMCOM_GROUP_INFO_DATA
    if NOMCOM_GROUP_INFO_DATA:
        return NOMCOM_GROUP_INFO_DATA

    nomcom_group_id = get_nomcom_group_id(force_metadata=force_metadata)
    nomcom_group_info_file = f"data/nomcom_group_info.json"
    if not force_metadata and os.path.exists(nomcom_group_info_file):
        with open(nomcom_group_info_file, "r", encoding="utf-8") as f:
            NOMCOM_GROUP_INFO_DATA = json.load(f)['objects']
            return NOMCOM_GROUP_INFO_DATA

    url = f"https://datatracker.ietf.org/api/v1/group/role/?group={nomcom_group_id}&limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    nomcom_group_info_data = response.json()

    os.makedirs(os.path.dirname(nomcom_group_info_file), exist_ok=True)
    with open(nomcom_group_info_file, "w", encoding="utf-8") as f:
        json.dump(nomcom_group_info_data, f, indent=4)
    print(f"Nomcom group info data downloaded and saved to {nomcom_group_info_file}")
    NOMCOM_GROUP_INFO_DATA = nomcom_group_info_data['objects']
    return NOMCOM_GROUP_INFO_DATA

def get_random_voting_members(force_metadata=False):
    """Gets the list of voting members and returns them in a random order."""
    nomcom_group_info = get_nomcom_group_info(force_metadata=force_metadata)
    voting_members = []
    for member in nomcom_group_info:
        if member['name'].endswith('/member/'):
            person_id = member['person'].strip('/').split('/')[-1]
            person_info = get_person_info_from_id(person_id, force_metadata=force_metadata)
            voting_members.append(person_info['name'])
    random.shuffle(voting_members)
    return voting_members

def is_email_in_nomcom(email, force_metadata=False):
    global NOMCOM_PERSON_IDS
    if not NOMCOM_PERSON_IDS:
        NOMCOM_PERSON_IDS = []
        nomcom_group_info = get_nomcom_group_info(force_metadata=force_metadata)
        for nomcom_member in nomcom_group_info:
            member_email_path = nomcom_member['email']
            member_email = member_email_path.strip('/').split('/')[-1]
            person_id = get_person_id_from_email(member_email, force_metadata=force_metadata)
            NOMCOM_PERSON_IDS.append(person_id)
    return get_person_id_from_email(email, force_metadata=force_metadata) in NOMCOM_PERSON_IDS


def get_active_nominees(force_metadata=False):
    global ACTIVE_NOMINEES_DATA
    if ACTIVE_NOMINEES_DATA:
        return ACTIVE_NOMINEES_DATA

    nominees = load_nominees(force_metadata=force_metadata)
    active_nominees = []
    for nominee in nominees:
        nominee_info = get_nominee_info(nominee['id'], force_metadata=force_metadata)
        if not nominee_info['positions']:
            continue
        has_accepted = False
        for state in nominee_info['positions'].values():
            if state == 'accepted':
                has_accepted = True
                break
        if has_accepted:
            active_nominees.append(nominee)

    ACTIVE_NOMINEES_DATA = active_nominees
    return active_nominees


def get_nominees_by_position(force_metadata=False):
    global NOMINEES_BY_POSITION_DATA
    if NOMINEES_BY_POSITION_DATA:
        return NOMINEES_BY_POSITION_DATA
    NOMINEES_BY_POSITION_DATA = {}
    for nominee in get_active_nominees(force_metadata=force_metadata):
        nominee_info = get_nominee_info(nominee['id'], force_metadata=force_metadata)
        for position, state in nominee_info['positions'].items():
            if state == 'accepted':
                if position not in NOMINEES_BY_POSITION_DATA:
                    NOMINEES_BY_POSITION_DATA[position] = []
                NOMINEES_BY_POSITION_DATA[position].append(nominee['id'])
    return NOMINEES_BY_POSITION_DATA


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    parser.add_argument("--info", action="store_true", help="Print info on each nominee, sorted.")
    parser.add_argument("--by-position", action="store_true", help="Print nominees by position.")
    parser.add_argument("--random-voting-members", action="store_true", help="Print a randomized list of voting members.")
    parser.add_argument("--email", help="Get info about a specific email address")
    parser.add_argument("nominee_id", nargs='?', help="Get info about a specific nominee")
    args = parser.parse_args()

    if args.info:
        print_nominee_info(force_metadata=args.force_metadata)
    elif args.by_position:
        print(json.dumps(get_nominees_by_position(force_metadata=args.force_metadata), indent=4))
    elif args.random_voting_members:
        print(json.dumps(get_random_voting_members(force_metadata=args.force_metadata), indent=4))
    elif args.email:
        print_info_from_email(args.email, force_metadata=args.force_metadata)
    elif args.nominee_id:
        print(json.dumps(get_nominee_info(args.nominee_id, force_metadata=args.force_metadata), indent=4))
    else:
        for nominee in load_nominees(force_metadata=args.force_metadata):
            get_nominee_info(nominee['id'], force_metadata=args.force_metadata)
        get_nominee_positions(force_metadata=args.force_metadata)
