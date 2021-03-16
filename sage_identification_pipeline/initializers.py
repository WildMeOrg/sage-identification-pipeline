from h2o_wave import Q

from .common import create_app_dirs, make_base_ui
from .user import AppUser
from .constants import example_images

def reset_pipeline_variables(q: Q):
    q.app.running_pipeline = False
    q.app.upload_complete = False
    q.app.detection_in_progress = False
    q.app.detection_complete = False
    q.app.classification_in_progress = False
    q.app.classification_complete = False
    q.app.identification_in_progress = False
    q.app.identification_complete = False

async def initialize_app(q: Q):
    # Initialize only once per app instance
    if q.app.initialized:
        return

    # Setup Cards and Users
    q.app.cards = {
        'crash_card': {},
    }
    q.app.users = {}

    # Setup the directory structure for the app in the local file system
    # create_app_dirs(q)

    # Perform all initialization specific to this app
    # await custom_app_init(q)

    # Mark the app as initialized
    q.app.initialized = True
    reset_pipeline_variables(q)
    q.app.api_prefix = 'https://demo.dyn.wildme.io'
    q.app.multi_select_index = 5
    q.app.max_path_length = 60

    print([image['path'] for image in example_images][0])
    print('./sage_identification_pipeline/assets/logo.png')

    logo_path_response = await q.site.upload(['./sage_identification_pipeline/assets/logo.png'])
    q.app.logo_path = logo_path_response[0]

    wave_paths = await q.site.upload([image['path'] for image in example_images])
    for p, example_image in zip(wave_paths, example_images):
        example_image.update({'wave_path': p})
    q.app.example_images = example_images


async def initialize_user(q: Q):
    user_id = q.auth.subject

    # If this user is logging in for the first time
    if user_id not in q.app.users:
        # Create a new user
        new_user = AppUser(
            user_id=user_id, email=q.auth.username, users_dir=q.app.users_dir
        )

        # Set newly created user as current user
        q.user.user = new_user

        # Add user to the list of app Users
        q.app.users[user_id] = new_user


async def initialize_client(q: Q):
    if q.client.initialized:
        return

    # Perform all initialization specific to this app
    # q.client.multi_select_icon = 'CheckboxComposite'
    # q.client.path = ['']
    # q.client.path_pointer = len(q.client.path) - 1
    # q.client.selected_objects = None
    # q.client.wave_file_paths = None

    # Crate the first view of the app
    await make_base_ui(q)

    # Mark the client as initialized
    q.client.initialized = True
