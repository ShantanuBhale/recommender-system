from flask import render_template, request
from app import app
from math import sqrt
import time
import datetime

def sim_distance(prefs,person1,person2):
 # Get the list of shared_items
 si={}
 for item in prefs[person1]:
     if item in prefs[person2]:
         si[item]=1
 # if they have no ratings in common, return 0
 if len(si)==0: return 0
 # Add up the squares of all the differences
 sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
 for item in prefs[person1] if item in prefs[person2]])
 return 1/(1+sum_of_squares)

def sim_pearson(prefs,p1,p2):
 # Get the list of mutually rated items
 si={}
 for item in prefs[p1]:
     if item in prefs[p2]: si[item]=1
         # Find the number of elements
 n=len(si)
 # if they are no ratings in common, return 0
 if n==0: return 0
 # Add up all the preferences
 sum1=sum([prefs[p1][it] for it in si])
 sum2=sum([prefs[p2][it] for it in si])
 # Sum up the squares
 sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
 sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
 # Sum up the products
 pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
 # Calculate Pearson score
 num=pSum-(sum1*sum2/n)
 den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
 if den==0: return 0
 r=num/den
 return r

def topMatches(prefs,person,n=5,similarity=sim_pearson):
 scores=[(similarity(prefs,person,other),other)
     for other in prefs if other!=person]
 # Sort the list so the highest scores appear at the top
 scores.sort( )
 scores.reverse( )
 return scores[0:n]

def getRecommendations(prefs,person,similarity=sim_pearson):
 totals={}
 simSums={}
 for other in prefs:
 # don't compare me to myself
     if other==person: continue
     sim=similarity(prefs,person,other)
     # ignore scores of zero or lower
     if sim<=0: continue
     for item in prefs[other]:
         # only score movies I haven't seen yet
         if item not in prefs[person] or prefs[person][item]==0:
             # Similarity * Score
             totals.setdefault(item,0)
             totals[item]+=prefs[other][item]*sim
             # Sum of similarities
             simSums.setdefault(item,0)
             simSums[item]+=sim
 # Create the normalized list
 rankings=[(total/simSums[item],item) for item,total in totals.items( )]
 # Return the sorted list
 rankings.sort( )
 rankings.reverse( )
 return rankings

def transformPrefs(prefs):
 result={}
 for person in prefs:
     for item in prefs[person]:
         result.setdefault(item,{})
         # Flip item and person
         result[item][person]=prefs[person][item]
 return result

def calculateSimilarItems(prefs,n=10):
 # Create a dictionary of items showing which other items they
 # are most similar to.
 result={}
 # Invert the preference matrix to be item-centric
 itemPrefs=transformPrefs(prefs)
 c=0
 for item in itemPrefs:
     # Status updates for large datasets
     c+=1
     if c%100==0: print "%d / %d" % (c,len(itemPrefs))
     # Find the most similar items to this one
     scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
     result[item]=scores
 return result

def getRecommendedItems(prefs,itemMatch,user):
 userRatings=prefs[user]
 scores={}
 totalSim={}
 # Loop over items rated by this user
 for (item,rating) in userRatings.items( ):
     # Loop over items similar to this one
     for (similarity,item2) in itemMatch[item]:
     # Ignore if this user has already rated this item
         if item2 in userRatings: continue
         # Weighted sum of rating times similarity
         scores.setdefault(item2,0)
         scores[item2]+=similarity*rating
         # Sum of all the similarities
         totalSim.setdefault(item2,0)
         totalSim[item2]+=similarity
 # Divide each total score by total weighting to get an average
 rankings=[(score/totalSim[item],item) for item,score in scores.items( )]
 # Return the rankings from highest to lowest
 rankings.sort( )
 rankings.reverse( )
 return rankings



def loadMovieLens(path='C:\\Users\\Shantannu\\Desktop\\recommender system\\ml'):
 # Get movie titles
 movies={}
 for line in open(path+'/u.item'):
     (id,title)=line.split('|')[0:2]
     movies[id]=title
     # Load data
     prefs={}
 for line in open(path+'/u.data'):
     (user,movieid,rating,ts)=line.split('\t')
     prefs.setdefault(user,{})
     prefs[user][movies[movieid]]=float(rating)
 return prefs
 
trained=0
itemsim=['__class__',
 '__cmp__',
 '__contains__',
 '__delattr__',
 '__delitem__',
 '__doc__',
 '__eq__',
 '__format__',
 '__ge__',
 '__getattribute__',
 '__getitem__',
 '__gt__',
 '__hash__',
 '__init__',
 '__iter__',
 '__le__',
 '__len__',
 '__lt__',
 '__ne__',
 '__new__',
 '__reduce__',
 '__reduce_ex__',
 '__repr__',
 '__setattr__',
 '__setitem__',
 '__sizeof__',
 '__str__',
 '__subclasshook__',
 'clear',
 'copy',
 'fromkeys',
 'get',
 'has_key',
 'items',
 'iteritems',
 'iterkeys',
 'itervalues',
 'keys',
 'pop',
 'popitem',
 'setdefault',
 'update',
 'values',
 'viewitems',
 'viewkeys',
 'viewvalues']
@app.route('/')

@app.route('/index',methods = ['POST', 'GET'])
def index():
   userno='87'
   prefs1m=loadMovieLens()
   
   global itemsim
   global trained
   if request.method == 'POST':
   		userno = request.form['nm']
   		if request.form['submit'] == 'Train':
   			prefs=getRecommendations(prefs1m,userno)[0:10]
   			before_time = datetime.datetime.now()
   			itemsim=calculateSimilarItems(prefs1m,n=20)
   			after_time = datetime.datetime.now()
   			tot_time=(after_time - before_time).seconds
   			trained=1
   			return render_template('index.html',
    				title='Home',
    				pref=prefs,
    				no=userno,
    				time=tot_time,
    				t='success',
    				check='user')

   		elif request.form['submit'] == 'Submit':
   			if request.form['optradio'] == 'user':
   				before_time = datetime.datetime.now()
   				prefs=getRecommendations(prefs1m,userno)[0:10]
   				after_time = datetime.datetime.now()
   				tot_time=(after_time - before_time).microseconds
   				tot_time=tot_time/1000
   				return render_template('index.html',
    					title='Home',
    					pref=prefs,
    					no=userno,
    					time=tot_time,
    					t='yes',
    					check='user')
   			elif (request.form['optradio'] == 'item' and trained == 1):
   				before_time = datetime.datetime.now()
   				prefsitem=getRecommendedItems(prefs1m,itemsim,userno)[0:10]
   				after_time = datetime.datetime.now()
   				tot_time=(after_time - before_time).microseconds
   				tot_time=tot_time/1000
   				return render_template('index.html',
    				title='Home',
    				pref=prefsitem,
    				no=userno,
    				time=tot_time,
    				t='yes',
    				check='item')
   			else:
   				prefs=getRecommendations(prefs1m,userno)[0:10]
   				return render_template('index.html',
    				title='Home',
    				pref=prefs,
    				no=userno,
    				time='0',
    				t='no',
    				check='item')

   else:
   		before_time = datetime.datetime.now()
   		prefs=getRecommendations(prefs1m,userno)[0:10]
   		after_time = datetime.datetime.now()
   		tot_time=(after_time - before_time).microseconds
   		tot_time=tot_time/1000
   		return render_template('index.html',
    			title='Home',
    			pref=prefs,
    			no=userno,
    			time=tot_time,
    			t='yes',
    			check='user')
   			

   
