import bottle
import makeagif.web

makeagif.web.start_workers()

application = bottle.default_app()