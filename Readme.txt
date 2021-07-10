#configuration steps

1. running virtual environment:
$venv\Scripts\activate

2. configure running arguments:
$set FLASK_APP=flaskr
$set FLASK_ENV=development

3. starting the platform:
$flask run 

#something to note

1. the back end of our platform is connected with local ganache simulated network.
the url of local network:"http://127.0.0.1:8545" can be changed to your net.

#test on platform
1. connecting to metamask account:
you can connect your metamask account with our platform by inputting it on the first page. Before that, it should also connect to the same blockchain network (local ganache network for example).

2. selecting function module:
you can choose to start with bug tutorial or challenge by clicking items in side bar.

3. tutorial part
in the bug list page, you are allowed to select the bug to continue.

3.1 specific bug tutorial
bug tutorial starts normally with static theory pages, read the content and click "Next Page".

3.2 specific bug tutorial continue...
in the dynamic interaction learning part, you should first read the guidance and then click buttons to interact as required.
After this tutorial, choose another or jump to challenge.

4. challenge part
click challenge status to initiate the main contract.
It gives address of all challenges and your rest time.

4. specific challenge
every challenge has different answer submitting way.
analyse and notice if you need to use other tools for solving problem, like remix is allowed.
make use of challenge contract address and it's source code to find answer.