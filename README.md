#ITEM-CATALOG(SUPERMART)


This application provides a list of categories available in the supermart and further list of items available for each given category.
This apllication performs CRUD functionality i.e. CREATE,READ,UPDATE,DELETE.
It uses oauth2 for secure logins.
It has a local permission system which allows only the logged in users to  make changes and others can only view items.
This application had JSON end points.




## INSTALLATION
-VirtualBox
-Vagrant
-Python 
-Flask

##FILES INCLUDED
-database.py
-supermart.db(without users)
-supermartwithusers.db
-SuperMartCatalog (python code)
-template (folder having all template files)
-static (folder having css files)
client_secrets.json (json file having client id)

## HOW TO RUN

Clone this repository
Open virtual machine  and change directory to the above one
Use vagrant up and vagrant ssh
Now run the python code using python3 SuperMartCatalog.py command
Open your browser and type url localhost:5000
To login and perform CRUD operations visit localhost:5000/login
Further you can use add,delete,edit commands after logingin.
Also JSON end points are added which can be used like localhost:5000/supermart/JSON

 

