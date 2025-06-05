# Trek Bike Watcher

This project monitors the Trek Bikes website for specific pre-owned bikes and sends email notifications when new bikes matching the criteria are found.

## Functionality

The script performs the following actions:

*   **Fetches Bike Data**: It regularly scrapes the Trek Bikes website for pre-owned road and mountain bikes.
*   **Filters Bikes**: Bikes are filtered based on specific criteria:
    *   Size: Looks for "58 cm" or "Large" frame sizes.
    *   Price Caps: Ensures road bikes are below $2500 and mountain bikes are below $2000.
    *   Exclusions: Ignores models containing "Medium/Large" or "Domane+".
*   **Tracks Seen Bikes**: It maintains a list of previously seen bike SKUs in the `trek_seen.json` file to identify new listings.
*   **Email Notifications**: If new bikes matching the criteria are found, an email notification is sent out detailing the new listings.

## Setup and Configuration

*   **Main Script**: The core logic is contained in `trek_watch.py`.
*   **Python Dependencies**: The script requires the following Python libraries:
    *   `requests`
    *   `pandas`
    These can be installed using pip:
    ```bash
    pip install requests pandas
    ```
*   **Email Notification Configuration**: To receive email notifications, you need to set up the following environment variables. These are typically configured as secrets in the GitHub repository for the automated workflow (see `.github/workflows/trek-watch.yml`).
    *   `SMTP_HOST`: The hostname of your SMTP server (e.g., `smtp.gmail.com`).
    *   `SMTP_PORT`: The port for the SMTP server (e.g., `465` for SSL, `587` for TLS). The script defaults to `465` if not set.
    *   `SMTP_USER`: The username for your SMTP account.
    *   `SMTP_PASS`: The password for your SMTP account.
    *   `MAIL_FROM`: The email address from which notifications will be sent.
    *   `MAIL_TO`: The email address to which notifications will be sent.

## Automated Workflow

This project uses GitHub Actions to automate the bike watching process. The workflow is defined in `.github/workflows/trek-watch.yml`.

*   **Scheduled Runs**: The script is automatically executed every 30 minutes.
*   **Manual Trigger**: The workflow can also be triggered manually from the Actions tab in the GitHub repository.
*   **State Tracking**: When new bikes are found and an email is sent, the `trek_seen.json` file is updated with the latest bike SKUs. The workflow then automatically commits and pushes this updated file to the repository.
*   **Credentials**: The email notification credentials (SMTP details, sender/receiver emails) are managed using GitHub encrypted secrets, ensuring they are not exposed in the codebase.

## Local Usage

To run the Trek Watcher script locally:

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2.  **Install Dependencies**:
    ```bash
    pip install requests pandas
    ```
3.  **Set Environment Variables**:
    Export the necessary environment variables for email notifications as described in the "Setup and Configuration" section. For example, in a bash shell:
    ```bash
    export SMTP_HOST="smtp.example.com"
    export SMTP_PORT="465"
    export SMTP_USER="your_email@example.com"
    export SMTP_PASS="your_password"
    export MAIL_FROM="sender@example.com"
    export MAIL_TO="recipient@example.com"
    ```
    (Note: Storing passwords directly in your shell history or scripts is not recommended for production environments. Consider using a secure way to manage them, like environment files not committed to git or a password manager.)
4.  **Run the Script**:
    ```bash
    python trek_watch.py
    ```
    The script will fetch the latest bike listings, compare them with `trek_seen.json` (which will be created if it doesn't exist), send an email if new bikes are found, and update `trek_seen.json`.

## License

This project does not currently have a license. Consider adding an open-source license like the [MIT License](https://opensource.org/licenses/MIT) if you plan to share or distribute this code.
