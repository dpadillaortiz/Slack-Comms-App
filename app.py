import os
import logging
from dotenv import load_dotenv
load_dotenv()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient

logging.basicConfig(level=logging.DEBUG)

import ssl
import certifi

# Get the path to the certifi CA bundle
ca_file_path = certifi.where()

# Create a custom SSL context
context = ssl.create_default_context(cafile=ca_file_path)

# Disable the strict verification flag
context.verify_flags &= ~ssl.VERIFY_X509_STRICT

# Initialize the WebClient with the custom SSL context
# This client will be used by the Bolt app for all API calls.
client = WebClient(
    token=os.getenv("SLACK_BOT_TOKEN"),
    ssl=context
)

# Initialization
app = App(token=os.getenv("SLACK_BOT_TOKEN"), client=client)

initial_view_blocks = [
    {
        "type": "input",
        "element": {
            "type": "rich_text_input",
            "action_id": "rich_text_input-action"
        },
        "block_id": "rich_text_input",
        "label": {
            "type": "plain_text",
            "text": "Message",
            "emoji": True
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Send message to:*"
        },
        "block_id": "multi_conversations_select",
        "accessory": {
            "type": "multi_conversations_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select conversations",
                "emoji": True
            },
            "action_id": "multi_conversations_select-action"
        }
    },
    {
        "type": "divider",
        "block_id": "divider_1"
    },
    {
        "type": "context",
        "block_id": "customization_hint",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "*Click here to customize sender identity and in-context call to action*"
            }
        ]
    },
    {
        "type": "actions",
        "block_id": "advanced_options",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Advanced options",
                    "emoji": True
                },
                "value": "click_me_123",
                "action_id": "advanced_options-action"
            }
        ]
    }
]

advanced_options_blocks = [
    {
        "type": "actions",
        "block_id": "customize_sender_identity",
        "elements": [
            {
                "type": "checkboxes",
                "options": [
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Do you need to customize the sender identity?*"
                        },
                        "description": {
                            "type": "plain_text",
                            "text": "I want to specify a custom sender name and a custom icon for my message, so that I can align the message's persona with its content.",
                            "emoji": True
                        },
                        "value": "value-0"
                    }
                ],
                "action_id": "customize_sender_identity-action"
            }
        ]
    },
    {
        "type": "actions",
        "block_id": "call_to_action",
        "elements": [
            {
                "type": "checkboxes",
                "options": [
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Do you need add in-context call to action?*"
                        },
                        "description": {
                            "type": "plain_text",
                            "text": "I want to add one or more clickable buttons with external links to my message, so that I can guide users to take a specific, immediate action.",
                            "emoji": True
                        },
                        "value": "value-1"
                    }
                ],
                "action_id": "call_to_action-action"
            }
        ]
    }
]

sender_identity_fields = [
    {
        "type": "divider",
        "block_id": "start_sender_identity_fields"
    },
    {
        "type": "input",
        "block_id": "sender_name",
        "element": {
            "type": "plain_text_input",
            "action_id": "plain_text_input-action",
            "placeholder": {
                "type": "plain_text",
                "text": "If left blank, the default name is used."
            }
        },
        "hint": {
            "type": "plain_text",
            "text": "A Slack bot's display name is limited to a maximum of 21 characters."
        },
        "optional": True,
        "label": {
            "type": "plain_text",
            "text": "Sender Name",
            "emoji": True
        }
    },
    {
        "type": "input",
        "block_id": "icon_url",
        "element": {
            "type": "plain_text_input",
            "action_id": "icon_url-action",
            "placeholder": {
                "type": "plain_text",
                "text": "If left blank, the default icon is used."
            }
        },
        "optional": True,
        "label": {
            "type": "plain_text",
            "text": "Icon URL",
            "emoji": True
        }
    },
    {
        "type": "divider",
        "block_id": "end_sender_identity_fields"
    }
]

call_to_action_dropdown = [
    {
        "type": "divider",
        "block_id": "start_call_to_action_dropdown"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "How many in-context call action will you need?"
        },
        "block_id": "call_to_action_dropdown",
        "accessory": {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select an item",
                "emoji": True
            },
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "1",
                        "emoji": True
                    },
                    "value": "1"
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "2",
                        "emoji": True
                    },
                    "value": "2"
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "3",
                        "emoji": True
                    },
                    "value": "3"
                }
            ],
            "action_id": "call_to_action_dropdown-action"
        }
    },
    {
        "type": "context",
        "block_id": "cta_buttons_hint",
        "elements": [
            {
                "type": "plain_text",
                "text": "You can add up to three actions.",
                "emoji": True
            }
        ]
    }
]

cta_buttons = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "CTA Button",
            "emoji": True
        },
        "block_id": "cta_button_header"
    },
    {
        "type": "input",
        "element": {
            "type": "plain_text_input",
            "action_id": "plain_text_input-action"
        },
        "block_id": "cta_button_text",
        "label": {
            "type": "plain_text",
            "text": "Button Text",
            "emoji": True
        },
        "hint": {
            "type": "plain_text",
            "text": "The character limit for button text in a Slack Block Kit button element is 75 characters. The text may appear truncated around 30 characters depending on the display device."
        }
    },
    {
        "type": "input",
        "element": {
            "type": "plain_text_input",
            "action_id": "plain_text_input-action"
        },
        "block_id": "cta_button_link",
        "label": {
            "type": "plain_text",
            "text": "Link",
            "emoji": True
        }
    }
]

def generate_cta_buttons(num_buttons):
    import copy
    blocks = []
    for i in range(num_buttons):
        cta_buttons_with_unique_block_id = copy.deepcopy(cta_buttons)
        # header
        cta_buttons_with_unique_block_id[0]["block_id"] = f"cta_button_header_{i+1}"
        cta_buttons_with_unique_block_id[0]["text"]["text"] = f"CTA Button {i+1}"
        # button text input
        cta_buttons_with_unique_block_id[1]["block_id"] = f"cta_button_text_{i+1}"
        cta_buttons_with_unique_block_id[1]["label"]["text"] = f"Button Text {i+1}"
        # button link input
        cta_buttons_with_unique_block_id[2]["block_id"] = f"cta_button_link_{i+1}"
        cta_buttons_with_unique_block_id[2]["label"]["text"] = f"Link {i+1}"
        # append to blocks
        blocks += cta_buttons_with_unique_block_id
    return blocks

@app.shortcut("bt_comms_shortcut")
def open_modal(ack, body, client, logger, shortcut):
    # Acknowledge the shortcut request
    ack()
    logger.info(body)
    # Call the views_open method using the built-in WebClient
    client.views_open(
        trigger_id=shortcut["trigger_id"],
        # A simple view payload for a modal
        view={
            "title": {
                "type": "plain_text",
                "text": "BT Comms App",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "type": "modal",
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "callback_id": "initial_view",
            "private_metadata": "",
            "blocks": initial_view_blocks
        }
    )


@app.action("advanced_options-action")
def handle_adv_options_button(ack, body, client, logger):
    ack()
    logger.info(body)

    client.views_push(
        trigger_id=body["trigger_id"],
        view={
            "private_metadata": "",
            "notify_on_close": True,
            "title": {
                "type": "plain_text",
                "text": "BT Comms App",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Next",
                "emoji": True
            },
            "type": "modal",
            "close": {
                "type": "plain_text",
                "text": "Go back",
                "emoji": True
            },
            "callback_id": "advanced_options_view",
            "blocks": advanced_options_blocks
        }
    )

# Handle view closed events for advanced options view
@app.view_closed("advanced_options_view")
def handle_view_closed_events(ack, body, logger):
    ack()
    logger.info(body)

@app.action("customize_sender_identity-action")
def handle_customize_sender_id_checkbox(ack, body, logger):
    ack()
    logger.info(body)
    advanced_options_blocks_with_cta_only = [*advanced_options_blocks, *call_to_action_dropdown]
    advanced_options_blocks_with_sender_only = [advanced_options_blocks[0], *sender_identity_fields, advanced_options_blocks[1]]
    advanced_options_blocks_with_sender_and_cta = [advanced_options_blocks[0], *sender_identity_fields, advanced_options_blocks[1], *call_to_action_dropdown]
    
    customize_sender_identity_selected = body["actions"][0]["selected_options"]
    call_to_action_selected = body["view"]["state"]["values"]["call_to_action"]["call_to_action-action"].get("selected_options", [])
    cta_buttons_selected = lambda: len(body["view"]["state"]["values"]) > 5

    logger.info("--------------------------------\n")
    if not customize_sender_identity_selected:
        logger.info("\nCHECKBOX: customize_sender_identity\nSTATUS: FALSE\n")
        if not call_to_action_selected:
            logger.info("\nCHECKBOX: call_to_action\nSTATUS: FALSE\n")
            # blocks = advanced_options_blocks
        if not cta_buttons_selected:
            logger.info("\nNO CTA BUTTONS DETECTED\n")
            blocks = advanced_options_blocks
        else:
            logger.info("\nCHECKBOX: call_to_action\nSTATUS: TRUE\n")
            logger.info("\nNO CTA BUTTONS DETECTED\n")
            #blocks = advanced_options_blocks_with_cta_only
            blocks = advanced_options_blocks_with_cta_only + generate_cta_buttons(int((len(body["view"]["state"]["values"]) - 5)/2))
    elif not call_to_action_selected:
        logger.info("\nCHECKBOX: customize_sender_identity\nSTATUS: TRUE\n")
        logger.info("\nCHECKBOX: call_to_action\nSTATUS: FALSE\n")
        blocks = advanced_options_blocks_with_sender_only
    elif not cta_buttons_selected:
        logger.info("\nCHECKBOX: call_to_action\nSTATUS: TRUE\n")
        logger.info("\nCTA BUTTONS DETECTED\n")
        blocks = advanced_options_blocks_with_sender_only + generate_cta_buttons(int((len(body["view"]["state"]["values"]) - 5)/2))
    else:
        logger.info("\nCHECKBOX: customize_sender_identity\nSTATUS: TRUE\n")
        logger.info("\nCHECKBOX: call_to_action\nSTATUS: TRUE\n")
        blocks = advanced_options_blocks_with_sender_and_cta


    

    logger.info("--------------------------------\n")

    client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        view={
            "private_metadata": "",
            "notify_on_close": True,
            "title": {
                "type": "plain_text",
                "text": "BT Comms App",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "type": "modal",
            "close": {
                "type": "plain_text",
                "text": "Go back",
                "emoji": True
            },
            "callback_id": "advanced_options_view",
            "blocks": blocks
        }
    )
    

@app.action("call_to_action-action")
def handle_call_to_action_checkbox(ack, body, logger):
    ack()
    logger.info(body)

    advanced_options_blocks_with_cta_only = [*advanced_options_blocks, *call_to_action_dropdown]
    advanced_options_blocks_with_sender_only = [advanced_options_blocks[0], *sender_identity_fields, advanced_options_blocks[1]]
    advanced_options_blocks_with_sender_and_cta = [advanced_options_blocks[0], *sender_identity_fields, advanced_options_blocks[1], *call_to_action_dropdown]
    
    call_to_action_selected = body["actions"][0]["selected_options"]
    customize_sender_identity_selected = body["view"]["state"]["values"]["customize_sender_identity"]["customize_sender_identity-action"].get("selected_options", [])
    if not call_to_action_selected:
        logger.info("--------------------------------\n")
        logger.info("call_to_action unchecked. removing call_to_action_dropdown\n")
        if not customize_sender_identity_selected:
            logger.info("--------------------------------\n")
            logger.info("also customize_sender_identity is unchecked. removing all extra fields\n")
            blocks = advanced_options_blocks
        else:
            blocks = advanced_options_blocks_with_sender_only
    elif not customize_sender_identity_selected:
        logger.info("--------------------------------\n")
        logger.info("also customize_sender_identity is unchecked. removing all extra fields\n")
        blocks = advanced_options_blocks_with_cta_only
    else:
        blocks = advanced_options_blocks_with_sender_and_cta
   
    client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        view={
            "private_metadata": "",
            "notify_on_close": True,
            "title": {
                "type": "plain_text",
                "text": "BT Comms App",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Next",
                "emoji": True
            },
            "type": "modal",
            "close": {
                "type": "plain_text",
                "text": "Go back",
                "emoji": True
            },
            "callback_id": "advanced_options_view",
            "blocks": blocks
        }
    )

@app.action("call_to_action_dropdown-action")
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)

    call_to_action_dropdown_selected = body["actions"][0]["selected_option"]
    call_to_action_requested_buttons = body["actions"][0]["selected_option"]["value"]
    call_to_action_button_blocks = generate_cta_buttons(int(call_to_action_requested_buttons))

    # Block kit combinations
    # advanced_options_blocks_with_cta_only = [*advanced_options_blocks, *call_to_action_dropdown]
    advanced_options_blocks_with_cta_buttons_only = [*advanced_options_blocks, *call_to_action_dropdown, *call_to_action_button_blocks]
    # advanced_options_blocks_with_sender_only = [advanced_options_blocks[0], *sender_identity_fields, advanced_options_blocks[1]]
    # advanced_options_blocks_with_sender_and_cta = [advanced_options_blocks[0], *sender_identity_fields, advanced_options_blocks[1], *call_to_action_dropdown]
    advanced_options_blocks_with_sender_and_cta_buttons = [advanced_options_blocks[0], *sender_identity_fields, advanced_options_blocks[1], *call_to_action_dropdown, *call_to_action_button_blocks]
    #state
    customize_sender_identity_selected = body["view"]["state"]["values"]["customize_sender_identity"]["customize_sender_identity-action"].get("selected_options", [])

    if call_to_action_dropdown_selected:
        if not customize_sender_identity_selected:
            logger.info("--------------------------------\n")
            logger.info("CUSTOMIZE SENDER ID unchecked.\n")
            logger.info(f"CALL TO ACTION DROPDOWN selected option: {call_to_action_dropdown_selected}\n")
            logger.info(f"REQUESTED NUMBER OF BUTTONS: {call_to_action_requested_buttons}\n")
            logger.info("Generating corresponding number of CTA button input fields...\n")
            blocks = advanced_options_blocks_with_cta_buttons_only
        else:
            logger.info("--------------------------------\n")
            logger.info(f"CALL TO ACTION DROPDOWN selected option: {call_to_action_dropdown_selected}\n")
            logger.info(f"REQUESTED NUMBER OF BUTTONS: {call_to_action_requested_buttons}\n")
            logger.info("Generating corresponding number of CTA button input fields...\n")
            blocks = advanced_options_blocks_with_sender_and_cta_buttons


    client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        view={
            "private_metadata": "",
            "notify_on_close": True,
            "title": {
                "type": "plain_text",
                "text": "BT Comms App",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Next",
                "emoji": True
            },
            "type": "modal",
            "close": {
                "type": "plain_text",
                "text": "Go back",
                "emoji": True
            },
            "callback_id": "advanced_options_view",
            "blocks": blocks
        }
    )


# Start Bolt app
if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
