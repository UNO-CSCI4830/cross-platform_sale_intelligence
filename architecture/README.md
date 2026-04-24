# Cross-platform Sale Intelligence Architecture

## Overview
* This file contains the description of the software architecture from three aspects - application architecture, structural design, and creational design. The system contains frontend, backend, and database component to create a comprehensive and user-friendly selling platform. 
---

## Design #1: Application Architecture - Modular Monolith
* Modular monolith is an architecture type that comprehends the "all-in-one" approach with a modular organization. It gives the developer the flexibility and scalability in developing a software. This architecture was selected because our team consists of students specialized in specific aspects within the software that lead to the modular development while aiming to develop a single product. It has allowed us to easily identify the code location by referring to the raw code it belongs to and organize the scripts. 
More information [here](https://www.geeksforgeeks.org/system-design/what-is-a-modular-monolith/)

The overall diagram is as shown below: Currently, there are three major components, but this structure will allow us to expand in a flexible manner due to clear organization.

![Modular_Monolith](architecture_diagram/ModularMonolith.jpeg)

* Frontend
This contains codes that is implemented to develop the frontend of the software. With applications of React App, we are able to develop a user interface that allows the sellers to have unified platform to manage their item listing across different selling platforms. This is where the user will interact with this software through the user interface.

* Backend
The backend mainly deals with the software components that ensures a smooth workflow in navigating the workflow. It manages the data retreived by different selling platform as well as management of the user information including user account creation and user authentication.

* Buying Database
This database incorporates the items listed on the platform in the PostgreSQL database. It allows sellers to manage item listing through flexible query options and reference pricing for pricing recommendation. 

---

## Design #2: Structural Design Pattern - Adapter Pattern
* Adapter pattern was selected due to the nature of this platoform - retieving information from other selling platforms and implement them all to develop a conprehensive software. We will be retreiving information from different selling platforms without modifying thier source code but incude it to the UI. 
More information [here](https://www.geeksforgeeks.org/system-design/adapter-pattern/).
The overall diagram is as shown below:
![Adapter_Pattern](architecture_diagram/AdapterPattern.jpeg)

Explanation:
* The 'Adapter' here is the API of the platform we refer to, and the adaptees are the information regarding each item on sale (i.e. price, condition, size etc.)

---

## Design #3: Creational Design Pattern - Factory Pattern
* Factory pattern was selected in implementing the the different selling platforms - mercari, poshmark, and ebay. Each platform information will be retrieved from designated API, and it will give us the flexibility to add new prodcts in each developmental step as well as in developing a tool that is user friendly.
More information [here](https://www.geeksforgeeks.org/system-design/factory-method-for-designing-pattern/).

The overall diagram is as shown below:
![Factory_Pattern](architecture_diagram/FactoryPattern.jpeg)

Explanation:
* The interface is where the item information will be connected from different platforms.
* In connecting with the selling platforms, we will be using API to retreive the information required. 


