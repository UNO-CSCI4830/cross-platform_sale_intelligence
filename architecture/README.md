# Cross-platform Sale Intelligence Architecture

## Overview
* This file contains the description of the software architecture from three aspects - application architecture, structural design, and creational design. The system contains frontend, backend, and database component to create a comprehensive and user-friendly selling platform. 
---

## Design #1: Application Architecture - Modular Monolith
* Modular monolith is an architecture type that comprehends the "all-in-one" approach with a modular organization. It gives the developer the flexibility and scalability in developing a software. This architecture was selected because out team consists of students specialized in certain domains within the software that lead to the modular development while aiming to develop a single product. It has allowed us to easily identify the code location by referring to the raw code it belongs to and organize the scripts. 
More information [here](https://www.geeksforgeeks.org/system-design/what-is-a-modular-monolith/)

The overall diagram is as shown below: Currently, there arethree major components, but this structure will allow us to expand in a flexible manner due to clear organization.

* Frontend
This contains the code that is implemented to develop the frontend of the software. With applications of React App, we are able to develop a user interface that allows the sellers to have unified platform to manage their item listing across different selling platforms.

* Backend
The backend mainly deals with the software components that ensures a smooth workflow in navigating the workflow. It manages the data retreived by different selling platform as well as management of the user information including user account creation and user authentication.

* Buying Database
This database incorporates the items listed on the platform in the PostgreSQL database. It allows sellers to manage item listing through flexible query options and reference pricing for pricing recommendation. 

---

## Design #2: Structural Design Pattern - Adapter Pattern
* Adapter pattern was selected because 

The overall diagram is as shown below:

Explanation:

---

## Design #3: Creational Design Pattern - Factory Pattern
* Factory pattern was selected because 

The overall diagram is as shown below:

Explanation:

