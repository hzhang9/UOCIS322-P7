# UOCIS322 - Project 7 #
Adding authentication and user interface to brevet time calculator service

## Recall Project 4

### Overview

Reimplement the RUSA ACP controle time calculator with Flask and AJAX.

### ACP controle times

Controls are points where a rider must obtain proof of passage, and control[e] times are the minimum and maximum times by which the rider must arrive at the location. In other words, essentially replacing the calculator here [https://rusa.org/octime_acp.html](https://rusa.org/octime_acp.html).   

## Recall Project 5

### Overview

Store control times from Project 4 in a MongoDB database.

### Difference with project 4

1. Add two buttons `Submit` and `Display` in the ACP calculator page.

2. Upon clicking the `Submit` button, the control times should be inserted into a MongoDB database.

3. Upon clicking the `Display` button, the entries from the database should be displayed in a new page.

4. Will shows error if inputed control distance is wrong or empty, detailed error response rule reference [https://rusa.org/octime_acp.html](https://rusa.org/octime_acp.html).

## Recall project 6

Project 6 has following four functionality. 

* 1.
    * "http://<host:port>/listAll" should return all open and close times in the database
    * "http://<host:port>/listOpenOnly" should return open times only
    * "http://<host:port>/listCloseOnly" should return close times only

* 2.
    * "http://<host:port>/listAll/csv" should return all open and close times in CSV format
    * "http://<host:port>/listOpenOnly/csv" should return open times only in CSV format
    * "http://<host:port>/listCloseOnly/csv" should return close times only in CSV format

    * "http://<host:port>/listAll/json" should return all open and close times in JSON format
    * "http://<host:port>/listOpenOnly/json" should return open times only in JSON format
    * "http://<host:port>/listCloseOnly/json" should return close times only in JSON format

* 3.
    * "http://<host:port>/listOpenOnly/csv?top=3" should return top 3 open times only (in ascending order) in CSV format 
    * "http://<host:port>/listOpenOnly/json?top=5" should return top 5 open times only (in ascending order) in JSON format
    * "http://<host:port>/listCloseOnly/csv?top=6" should return top 5 close times only (in ascending order) in CSV format
    * "http://<host:port>/listCloseOnly/json?top=4" should return top 4 close times only (in ascending order) in JSON format

* 4.
    * A consumer programs.

## Functionality of this project

In this project, willing to add the following functionalities:

### Part 1: Authenticating the services 

- POST **/register**

Registers a new user. On success a status code 201 is returned. The body of the response contains a JSON object with the newly added user. On failure status code 400 (bad request) is returned. Note: The password is hashed before it is stored in the database. Once hashed, the original password is discarded. Your database should have three fields: id (unique index), username and password for storing the credentials.

- GET **/token**

Returns a token. This request must be authenticated using a HTTP Basic Authentication (see `DockerAuth/password.py` and `DockerAuth/testToken.py`). On success a JSON object is returned with a field `token` set to the authentication token for the user and a field `duration` set to the (approximate) number of seconds the token is valid. On failure status code 401 (unauthorized) is returned.

- GET **/RESOURCE-YOU-CREATED-IN-PROJECT-6**

Return a protected <resource>, which is basically what you created in project 6. This request must be authenticated using token-based authentication only (see `DockerAuth/testToken.py`). HTTP password-based (basic) authentication is not allowed. On success a JSON object with data for the authenticated user is returned. On failure status code 401 (unauthorized) is returned.

### Part 2: User interface

The goal of this part of the project is to create frontend/UI for Brevet app using Flask-WTF and Flask-Login introduced in lectures. You frontend/UI should use the authentication that you created above. In addition to creating UI for basic authentication and token generation, you will add three additional functionalities in your UI: a) registration, b) login, c) remember me, d) logout.

## How to use?

Entry consumer programs, then register and log in by tips for using.

## Identifying Information

Author: Haoran Zhang, hzhang9@uoregon.edu
