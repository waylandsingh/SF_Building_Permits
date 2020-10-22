from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap

#requests library
import requests
#simplejson to parse
import simplejson as json
import pandas as pd
import numpy as np
import pandas as pd
import dill

classifierOTC = dill.load(open('models/classifierOTC.dill','rb'))
regressor_not_OTC = dill.load(open('models/not_OTC_regressor.dill','rb'))

#bokeh to plot the dataframe
#from bokeh.plotting import figure, output_file, show, ColumnDataSource, save, output_notebook
#from bokeh.models import Range1d
#from bokeh.embed import components #for embedable code
SFNEIGH = ['Bayview Hunters Point','Bernal Heights','Castro/Upper Market','Chinatown','Excelsior','Financial District/South Beach','Glen Park','Haight Ashbury','Hayes Valley','Inner Richmond','Inner Sunset','Japantown','Lakeshore','Lincoln Park','Lone Mountain/USF','Marina','McLaren Park','Mission','Mission Bay','Nob Hill','Noe Valley','North Beach','Oceanview/Merced/Ingleside','Outer Mission','Outer Richmond','Pacific Heights','Portola','Potrero Hill','Presidio','Presidio Heights','Russian Hill','Seacliff','South of Market','Sunset/Parkside','Tenderloin','Twin Peaks','Visitacion Valley','West of Twin Peaks','Western Addition']
OTC_H = 'Same Day (OTC) Approval'
OTC_MSG =  'It looks like your project should be approved immediately!'

app = Flask(__name__)
Bootstrap(app)

app.vars = {} #dict to store variables input in form

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html/', neighs=SFNEIGH, 
                           pred_h='',pred_msg1='',pred_msg2='')
#    return render_template('input_info.html', neighs=SFNEIGH)


@app.route('/info_received', methods=['POST'])
def info_received():
    #save info from html form into app.vars to be used in function calls
    app.vars['description'] = request.form['description'].lower()
    #santize and check input
    app.vars['neighborhood'] = request.form['neighborhood']
    app.vars['cost'] = request.form['cost']
    
    #consider cleaning the addresses input with usaaddress?
    app.vars['units_change'] = request.form['units'] 
    app.vars['address'] = request.form['address']
    
    #verify sane input, else re-render page
    
    # NOT USED FOR NOW look up address in assessor table to get the other features
   
    otc_flag = classifierOTC.predict([app.vars['description']])[0]
    
    #if zero day, return the page for OTC approvals
    if otc_flag != 0:
        plist = [[app.vars['description'],
                 app.vars['neighborhood'],
                 app.vars['cost'],
                 app.vars['units_change']]]
        d = int(regressor_not_OTC.predict(plist)[0])
        multi_h = f'Approval Estimate: {d} days'
        multi_msg1 = 'It looks like your project will take longer to approve.'
        multi_msg2 = 'Consult with your contractor and SFBD for more information.'
        return render_template('index.html/', neighs=SFNEIGH,
                               pred_h=multi_h, pred_msg1=multi_msg1,
                               pred_msg2=multi_msg2)
#        return render_template('not_OTC.html',days=d)
    
    #else nonzero, jam it into the regressor and return a prediction
    elif otc_flag == 0:
        return render_template('index.html/', neighs=SFNEIGH,
                               pred_h=OTC_H, pred_msg1=OTC_MSG,
                               pred_msg2='')
#        return render_template('OTC_page.html')
    else:
        return 'fix me!'
    # for later, when boostrap is added
#    return render_template('bootstrap.html')



@app.route('/info_received', methods=['GET'])
def back_to_input():
    return redirect('/')

if __name__ == '__main__':
  app.run(debug=True,port=50000)
    
