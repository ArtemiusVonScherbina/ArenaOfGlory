# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render,get_object_or_404,render_to_response,redirect
from django.http import JsonResponse, HttpResponse,HttpResponseRedirect
from .models import Room,Character
import random
from datetime import datetime
# Create your views here.
# Функция для перехода на шаблон комнаты
def go_to_room(request, id=None):
	status = True
	instance = get_object_or_404(Room, id=id)
	if instance.data_end:
		status = False
	players = Character.objects.filter(room=instance)
	context = {
		"instance": instance,
		"players": players,
		"status":status,
	}
	return render(request, "fight_room.html", context)
@csrf_protect
def show_rooms(request):
	# В случае если метода POST
	if request.method == "POST":
		# получаем данные из запроса
		name_room = request.POST.get("nameRoom")
		name_player = request.POST.get("nameChar")
		race_player = request.POST.get("raceChar")
		name_enemy = request.POST.get("nameEnem")
		race_enemy = request.POST.get("raceEnem")
		# Создаем комнату и сохраняем ее в базе данных
		room = Room(name=name_room,game_type = "SP")
		room.save()
		# Создаем игрока и врага, далие сохранияе в базе данных
		players = Character(room=room, name = name_player, race =race_player)
		enemy = Character(room=room, name = name_enemy, race =race_enemy)
		players.save()
		enemy.save()
		# Переходим на страницу с комнаты.
		return HttpResponseRedirect(room.get_absolute_url())
	rooms = Room.objects.all()
	characters = Character.objects.all()
	context = {
		"title":"Rooms",
		"rooms": rooms,
		"characters":characters,
		# Добавил поле races для правильного оторажения расы
		"races":Character.RACE
	}
	return render(request,"main_menu.html",context)
def create_players(request):
	context = {
		"title":"Create players",
		"races":Character.RACE	
	}
	return render(request,"characters_create.html", context)
def fight_room(request):
	context = {"title":"Fight room"}
	return render(request,"fight_room.html", context)
def attack(request):
	if request.is_ajax():
		# Получить id от запроса
		player_id = request.GET.get("playerId")

		enemy_id = request.GET.get("enemyId")
		# соверщить поиск в базе по id чтобы найти персонажа
		player = Character.objects.get(id=player_id)
		enemy = Character.objects.get(id=enemy_id)
		part_enemy = request.GET.get("partEnemy")
		part_player = request.GET.get("partPlayer")
		roomer_id=request.GET.get("id")
		print(roomer_id)
		room = Room.objects.get(id=int(roomer_id))
		enemy.choice_target(random.randint(0,4))
		enemy.body_block(random.randint(0,4))
		player.choice_target(int(part_enemy))
		player.body_block(int(part_player))
		enemy.attack(player)
		player.attack(enemy)
		# Сохранить новые значения в базе данных
		enemy.save()
		player.save()

		context = {
			"healthEnemy": enemy.health,
			"healthPlayer": player.health
		}
		if ((enemy.health<=0) or (player.health<=0)):
			room.data_end = datetime.now()
			context.update({"url":room.get_result()})
		print (context)
		jsresp = JsonResponse(context)
		
		return HttpResponse(jsresp.content, content_type='text/html')

	
def fight_result(request,id):
	room = Room.objects.get(id=id)
	players = Character.objects.filter(room = room)
	if (players[0].health>players[1].health):
		result_str="Congatulations! You, "+players[0].name+", defeated your enemy and won!"
	elif (players[0].health<players[1].health):
		result_str="You lost! You, "+players[0].name+", was defeated by your enemy and died!"
	elif (players[0].health==players[1].health):
		result_str="Draw! You, "+players[0].name+", killed your enemy at the same time as he killed you!"
	context = {
			"result_str": result_str,
		}
	return render(request,"result.html", context)