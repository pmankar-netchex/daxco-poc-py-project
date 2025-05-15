## Payroll integration app

Frontend requirements  -
   i. User can upload or drag and drop CSV in the input format, as mentioned in the input_format.csv
   ii. user also selects fields like company from a drop_down list as per selected company Company_code is passed down in JSON object. Along with additional information integration_type=DAXCO and upload_type=PAYROLL
   iii. Once import is complete, user clicks on validate button to trigger validation workflow
   iv. This click triggers a backend API call where company_code is sent in object and csv filed as passed on as uploaded. Backend API will do validations, and return results to frontend.
   v. Post validation click user is redirected to validation page, where user will see validation data in tabular format
   vi. User can make manual edits in any row, all the invalid rows are highlighted for user to act, user can delete entire invalid row as well
   vii. post manual corrections, if there are not validation errors, user can click on re-validate and submit button
   viii. After clicking on re-validate and submit, if there are no issues, user will be redirected to validation success page, here user can see download button to download final transformed file
   ix. After clicking on re-validate and submit, if there are still validation issues, user stays on same page where new validation errors are displayed for user to correct from

Backend requirements - 
   i. Frontend will trigger a trigger to a backend API which will host backend logic
   ii. Frontend will send file as csv and json object
   iii. Backend will expect file in input_format.csv and convert it into formatted_output.csv
   iv. if there multiple employee codes found, user should be seeing drop-down to select from
   v. if there are no employee code found, user will enter code manually
   vi. if any column is missing, or any validation fails show error that file-format not suported
   vii. scheduled_payroll field should be numeric as it's payroll value in dollars

Frontend should use react app with mui and simple css
Backend needs to be logic app, as I want to reuse most of these things for more input formats
