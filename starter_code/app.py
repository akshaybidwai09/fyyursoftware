#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask_migrate import Migrate
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from forms import VenueForm, ArtistForm, ShowForm
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


# TODO: connect to a local postgresql database
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
moment = Moment(app)
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Venue is the parent (one-to-many) of a Show (Artist is also a foreign key, in def. of Show)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))


    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

# Artist is the parent (one-to-many) of a Show (Venue is also a foreign key, in def. of Show)
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='Artist', lazy=True)   

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)   

    # Foreign key is the tablename.pk
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)   
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time} artist_id={self.artist_id} venue_id={self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)
app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
#db.create_all()
@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venue = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  for venues in venue:
    venues_city_state = db.session.query(Venue.id, Venue.name).filter(Venue.city == venues[0]).filter(Venue.state == venues[1])
    data.append({
      "city": venues[0],
      "state": venues[1],
      "venues": venues_city_state
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venue = db.session.query(Venue).filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
  data = []
  for venues in venue:
    num_upcoming_shows = Show.query.filter(Show.venue_id == Venue.id, Show.start_time > datetime.now()).count()
    data.append({
      "id": venues.id,
      "name": venues.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  response={
    "count": len(data), 
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  list_shows = db.session.query(Show).filter(Show.venue_id == venue_id)
  past_shows = []
  upcoming_shows = []
  for show in list_shows:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    show_add = {
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime('%m/%d/%Y')
        }
    if (show.start_time < datetime.now()):
        past_shows.append(show_add)
    else:
        upcoming_shows.append(show_add)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    venues = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(venues)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Venue ' + request.form['name'] + ' was not listed')
  finally:
    db.session.close()  
  return redirect(url_for('index'))


  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted')
  except:
    db.session.rollback()
    flash('Venue ' + venue.name + ' was not deleted')
  finally:
    db.session.close()
  return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form, obj=venue)
  try:
    form.populate_obj(venue)
    db.session.commit()
    flash("Venue is successfully edited")
  except:
    db.session.rollback()
    flash("An error occurred!")
  return redirect(url_for('show_venue', venue_id=venue_id))

################################################################################################################################################
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artist = Artist.query.all()
  for artists in artist:
    data.append({
      "id": artists.id,
      "name": artists.name
    })
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  artist = db.session.query(Artist).filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
  data = []
  for artists in artist:
    num_upcoming_shows = Show.query.filter(Show.artist_id == Artist.id, Show.start_time > datetime.now()).count()
    data.append({
      "id": artists.id,
      "name": artists.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  list_shows = db.session.query(Show).filter(Show.artist_id == artist_id)
  past_shows = []
  upcoming_shows = []
  for show in list_shows:
    venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()
    show_add = {
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y')
    }
    if (show.start_time < datetime.now()):
      past_shows.append(show_add)
    else:
      print(show_add, file=sys.stderr)
      upcoming_shows.append(show_add)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  try:
    form.populate_obj(artist)
    db.session.commit()
    flash("Artist is successfully edited")
  except:
    db.session.rollback()
    flash("An error occurred!")
  return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  try:
    artists = Artist(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    genres = form.genres.data,
    facebook_link = form.facebook_link.data,
    image_link = form.image_link.data,
    website_link = form.website_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data
  )
    db.session.add(artists)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Artist ' + request.form['name'] + ' was not listed')
  finally:
    db.session.close()  
  return redirect(url_for('index'))
#################################################################################################################################################
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
  form = ShowForm(request.form)

  artist_id = form.artist_id.data
  venue_id = form.venue_id.data
  start_time = form.start_time.data

  error_in_insert = False
  
  try:
    new_show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
    db.session.add(new_show)
    db.session.commit()
  except ValueError as e:
    error_in_insert = True
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  if error_in_insert:
    flash(f'An error occurred.  Show could not be listed.')
    print("Error in create_show_submission()")
  else:
    flash('Show was successfully listed!')
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
