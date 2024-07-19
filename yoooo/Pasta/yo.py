from kivy.clock import Clock
def my_callback(dt):
    print("oi")
# invoca a função my_callback a cada 0,5 segundos
event = Clock.schedule_interval(my_callback, 0.5)