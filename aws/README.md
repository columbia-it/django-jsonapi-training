# Jian's rough notes.

TODO: edit

- In the top folder of your project there are two files: zappa_setting.json and dev_zappa_setting.py
  These two are purely for zappa to use.  If you don't use Zappa, these two files won't be used by Django at all, therefore they won't harm your application.

- In the ../aws/rds directory there are 4 files:
  rds_data_client.py 
  rds_cfn_template.yaml 
  dev-env.sh 
  deploy_rds_stack.sh
You may ignore these files as they aren't  participated the Zappa deployment at all. Why here? I simply feel these pieces of code may come in handy.

For example,  the rds_cfn_template.yaml is easier to create rds, master user, as well as the secret etc.
And rds_data_client.py may be as an example of alternative db housework otherwise you may use Django management command for db(if you want to drop tables during dev.)   All these files should not interfere with your code if not using Zappa.


I also realize that  zappa_setting.json and dev-env.sh are too specific meaning from user to user could be different,
therefore I am not sure if it makes sense to merge your original code.  Perhaps you don't need the MR at all.


