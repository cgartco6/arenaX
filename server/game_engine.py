import random
import time
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# In-memory data stores (replace with database in production)
active_battles: Dict[str, dict] = {}
player_stats: Dict[str, dict] = {}
tournaments: Dict[str, dict] = {}
battle_queue: List[str] = []  # Player IDs waiting for matchmaking
ai_players: List[dict] = []

class GameEngine:
    def __init__(self):
        # Initialize AI players
        self.initialize_ai_players()
        # Start background tasks
        asyncio.create_task(self.matchmaking_loop())
        asyncio.create_task(self.tournament_scheduler())

    def initialize_ai_players(self):
        """Create AI opponents with varying difficulty levels"""
        difficulties = ["easy", "medium", "hard", "elite"]
        for i in range(20):
            ai_id = f"ai_{i+1}"
            difficulty = random.choice(difficulties)
            
            # Base stats
            stats = {
                "level": random.randint(1, 50),
                "health": 100,
                "damage": random.randint(10, 30),
                "armor": random.randint(5, 20),
                "speed": random.randint(1, 10),
            }
            
            # Adjust based on difficulty
            if difficulty == "easy":
                stats["health"] = 80
                stats["damage"] = max(10, stats["damage"] - 5)
            elif difficulty == "hard":
                stats["health"] = 120
                stats["damage"] += 5
            elif difficulty == "elite":
                stats["health"] = 150
                stats["damage"] += 10
                stats["armor"] += 5
            
            ai_players.append({
                "id": ai_id,
                "name": f"{difficulty.capitalize()} Mech #{i+1}",
                "difficulty": difficulty,
                "stats": stats,
                "is_ai": True
            })
    
    async def matchmaking_loop(self):
        """Continuously match players with opponents"""
        while True:
            try:
                if len(battle_queue) >= 2:
                    # Match two players
                    player1_id = battle_queue.pop(0)
                    player2_id = battle_queue.pop(0)
                    await self.start_pvp_battle(player1_id, player2_id)
                
                # Match players with AI if queue is stagnant
                elif battle_queue and len(ai_players) > 0:
                    player_id = battle_queue.pop(0)
                    ai_player = random.choice(ai_players)
                    await self.start_pve_battle(player_id, ai_player["id"])
                
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"Matchmaking error: {str(e)}")
                await asyncio.sleep(10)

    async def tournament_scheduler(self):
        """Manage tournament events"""
        while True:
            try:
                now = datetime.utcnow()
                
                # Create daily tournament at 20:00 UTC
                if now.hour == 20 and now.minute == 0:
                    if not any(t["start_time"].date() == now.date() for t in tournaments.values()):
                        await self.create_tournament("Daily Championship", "medium", 100)
                
                # Create weekly tournament on Sundays
                if now.weekday() == 6 and now.hour == 18 and now.minute == 0:  # Sunday
                    if not any(t["name"] == "Weekly Grand Tournament" and 
                               t["start_time"].date() == now.date() for t in tournaments.values()):
                        await self.create_tournament("Weekly Grand Tournament", "hard", 500)
                
                # Start scheduled tournaments
                for tournament in list(tournaments.values()):
                    if tournament["status"] == "scheduled" and now >= tournament["start_time"]:
                        await self.start_tournament(tournament["id"])
                
                # End running tournaments
                for tournament in list(tournaments.values()):
                    if tournament["status"] == "running" and now >= tournament["end_time"]:
                        await self.end_tournament(tournament["id"])
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Tournament scheduler error: {str(e)}")
                await asyncio.sleep(120)

    async def start_battle(self, player_data: dict) -> dict:
        """Initiate a battle for a player"""
        player_id = player_data["player_id"]
        
        # Ensure player exists
        if player_id not in player_stats:
            self.initialize_player(player_id)
        
        # Add to matchmaking queue
        if player_id not in battle_queue:
            battle_queue.append(player_id)
        
        return {
            "status": "queued",
            "message": "Looking for opponent...",
            "queue_position": len(battle_queue)
        }

    async def start_pvp_battle(self, player1_id: str, player2_id: str):
        """Start a player vs player battle"""
        battle_id = f"battle_{uuid.uuid4().hex}"
        
        battle_data = {
            "id": battle_id,
            "player1": player1_id,
            "player2": player2_id,
            "start_time": datetime.utcnow(),
            "status": "active",
            "type": "pvp",
            "events": [],
            "winner": None
        }
        
        active_battles[battle_id] = battle_data
        
        # Notify players (in production, this would use WebSockets)
        self.log_battle_event(battle_id, "Battle started!")
        self.log_battle_event(battle_id, f"{self.get_player_name(player1_id)} vs {self.get_player_name(player2_id)}")
        
        # Simulate battle
        asyncio.create_task(self.simulate_battle(battle_id))

    async def start_pve_battle(self, player_id: str, ai_id: str):
        """Start a player vs AI battle"""
        battle_id = f"battle_{uuid.uuid4().hex}"
        ai_player = next((ai for ai in ai_players if ai["id"] == ai_id), None)
        
        if not ai_player:
            ai_player = random.choice(ai_players)
        
        battle_data = {
            "id": battle_id,
            "player1": player_id,
            "player2": ai_player["id"],
            "ai_data": ai_player,
            "start_time": datetime.utcnow(),
            "status": "active",
            "type": "pve",
            "events": [],
            "winner": None
        }
        
        active_battles[battle_id] = battle_data
        
        # Notify player
        self.log_battle_event(battle_id, "Battle started!")
        self.log_battle_event(battle_id, f"{self.get_player_name(player_id)} vs {ai_player['name']}")
        
        # Simulate battle
        asyncio.create_task(self.simulate_battle(battle_id))

    async def simulate_battle(self, battle_id: str):
        """Simulate a battle with turns and events"""
        battle = active_battles.get(battle_id)
        if not battle:
            return
        
        # Get player stats
        player1 = self.get_player_stats(battle["player1"])
        player2 = self.get_player_stats(battle["player2"])
        
        # AI battles use different stats
        if battle["type"] == "pve":
            player2 = battle["ai_data"]["stats"]
        
        # Battle loop
        turn = 1
        max_turns = 20  # Prevent infinite battles
        
        while turn <= max_turns and player1["health"] > 0 and player2["health"] > 0:
            # Player 1 attacks Player 2
            damage = self.calculate_damage(player1, player2)
            player2["health"] = max(0, player2["health"] - damage)
            self.log_battle_event(
                battle_id,
                f"Turn {turn}: {self.get_player_name(battle['player1'])} hits " +
                f"{self.get_player_name(battle['player2'])} for {damage} damage!"
            )
            
            if player2["health"] <= 0:
                battle["winner"] = battle["player1"]
                break
                
            # Player 2 attacks Player 1
            damage = self.calculate_damage(player2, player1)
            player1["health"] = max(0, player1["health"] - damage)
            self.log_battle_event(
                battle_id,
                f"Turn {turn}: {self.get_player_name(battle['player2'])} hits " +
                f"{self.get_player_name(battle['player1'])} for {damage} damage!"
            )
            
            if player1["health"] <= 0:
                battle["winner"] = battle["player2"]
                break
                
            turn += 1
            await asyncio.sleep(1)  # Simulate time between turns
        
        # Determine winner if battle timed out
        if not battle["winner"]:
            if player1["health"] > player2["health"]:
                battle["winner"] = battle["player1"]
            elif player2["health"] > player1["health"]:
                battle["winner"] = battle["player2"]
            else:
                battle["winner"] = "draw"
        
        # Battle conclusion
        battle["status"] = "completed"
        battle["end_time"] = datetime.utcnow()
        battle["duration"] = (battle["end_time"] - battle["start_time"]).total_seconds()
        
        if battle["winner"] == "draw":
            self.log_battle_event(battle_id, "Battle ended in a draw!")
        else:
            self.log_battle_event(
                battle_id,
                f"{self.get_player_name(battle['winner'])} wins the battle!"
            )
        
        # Process rewards
        asyncio.create_task(self.process_battle_rewards(battle_id))

    def calculate_damage(self, attacker: dict, defender: dict) -> int:
        """Calculate damage with random variation and armor reduction"""
        base_damage = attacker["damage"]
        variation = random.randint(-5, 5)
        damage = max(1, base_damage + variation - defender["armor"])
        return damage

    async def process_battle_rewards(self, battle_id: str):
        """Assign rewards and update player stats after battle"""
        battle = active_battles.get(battle_id)
        if not battle:
            return
        
        # Base rewards
        xp_reward = 50
        credit_reward = 25
        
        # PvP rewards
        if battle["type"] == "pvp":
            xp_reward = 100
            credit_reward = 50
            
            if battle["winner"] != "draw":
                # Winner gets bonus
                winner_id = battle["winner"]
                player_stats[winner_id]["xp"] += 50
                player_stats[winner_id]["credits"] += 25
                player_stats[winner_id]["wins"] += 1
                
                # Loser gets less
                loser_id = battle["player1"] if winner_id == battle["player2"] else battle["player2"]
                player_stats[loser_id]["xp"] += 20
                player_stats[loser_id]["credits"] += 10
                player_stats[loser_id]["losses"] += 1
            else:
                # Draw rewards
                player_stats[battle["player1"]]["xp"] += 40
                player_stats[battle["player1"]]["credits"] += 20
                player_stats[battle["player1"]]["draws"] += 1
                
                player_stats[battle["player2"]]["xp"] += 40
                player_stats[battle["player2"]]["credits"] += 20
                player_stats[battle["player2"]]["draws"] += 1
        
        # PvE rewards
        elif battle["type"] == "pve":
            if battle["winner"] == battle["player1"]:  # Player won
                difficulty = battle["ai_data"]["difficulty"]
                
                # Difficulty modifiers
                if difficulty == "easy":
                    xp_multiplier = 0.8
                    credit_multiplier = 0.8
                elif difficulty == "medium":
                    xp_multiplier = 1.0
                    credit_multiplier = 1.0
                elif difficulty == "hard":
                    xp_multiplier = 1.3
                    credit_multiplier = 1.3
                else:  # elite
                    xp_multiplier = 1.8
                    credit_multiplier = 1.8
                
                player_stats[battle["player1"]]["xp"] += int(xp_reward * xp_multiplier)
                player_stats[battle["player1"]]["credits"] += int(credit_reward * credit_multiplier)
                player_stats[battle["player1"]]["pve_wins"] += 1
            else:  # Player lost to AI
                player_stats[battle["player1"]]["xp"] += 10
                player_stats[battle["player1"]]["credits"] += 5
                player_stats[battle["player1"]]["pve_losses"] += 1
        
        # Check for level up
        for player_id in [battle["player1"], battle["player2"]]:
            if player_id in player_stats:
                self.check_level_up(player_id)
        
        # Clean up after delay
        await asyncio.sleep(30)  # Keep battle data for 30 seconds
        if battle_id in active_battles:
            del active_battles[battle_id]

    def check_level_up(self, player_id: str):
        """Check if player has enough XP to level up"""
        player = player_stats[player_id]
        xp_needed = self.xp_for_level(player["level"])
        
        if player["xp"] >= xp_needed:
            player["level"] += 1
            player["xp"] -= xp_needed
            player["skill_points"] += 1
            return True
        return False

    def xp_for_level(self, level: int) -> int:
        """Calculate XP needed for a level"""
        return 100 * (level ** 2) + 500

    async def create_tournament(self, name: str, difficulty: str, entry_fee: int):
        """Create a new tournament"""
        tournament_id = f"tournament_{uuid.uuid4().hex}"
        start_time = datetime.utcnow() + timedelta(hours=1)
        
        tournament = {
            "id": tournament_id,
            "name": name,
            "difficulty": difficulty,
            "entry_fee": entry_fee,
            "start_time": start_time,
            "end_time": start_time + timedelta(hours=2),
            "status": "scheduled",
            "participants": [],
            "matches": [],
            "prize_pool": 0,
            "sponsor": self.get_random_sponsor(),
            "winner": None
        }
        
        tournaments[tournament_id] = tournament
        return tournament

    async def start_tournament(self, tournament_id: str):
        """Start a scheduled tournament"""
        tournament = tournaments.get(tournament_id)
        if not tournament or tournament["status"] != "scheduled":
            return
        
        tournament["status"] = "running"
        tournament["start_time"] = datetime.utcnow()
        tournament["end_time"] = datetime.utcnow() + timedelta(hours=2)
        
        # Initialize prize pool
        tournament["prize_pool"] = tournament["entry_fee"] * len(tournament["participants"])
        
        # Create tournament bracket
        self.create_tournament_bracket(tournament_id)
        
        # Start first round
        await self.run_tournament_round(tournament_id)

    async def run_tournament_round(self, tournament_id: str):
        """Run the next round of tournament matches"""
        tournament = tournaments.get(tournament_id)
        if not tournament or tournament["status"] != "running":
            return
        
        # Get current round
        current_round = 1
        if tournament["matches"]:
            current_round = max(m["round"] for m in tournament["matches"]) + 1
        
        # Get players for this round
        if current_round == 1:
            players = tournament["participants"]
        else:
            # Winners from previous round
            players = [
                m["winner"] for m in tournament["matches"] 
                if m["round"] == current_round - 1 and m["winner"]
            ]
        
        # Create matches for this round
        matches = []
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                match_id = f"match_{uuid.uuid4().hex}"
                matches.append({
                    "id": match_id,
                    "player1": players[i],
                    "player2": players[i+1],
                    "round": current_round,
                    "status": "scheduled",
                    "winner": None
                })
        
        tournament["matches"].extend(matches)
        
        # Run matches
        for match in matches:
            await self.run_tournament_match(tournament_id, match["id"])
            await asyncio.sleep(1)  # Space out matches
        
        # Check if tournament should end
        if len(players) <= 2:
            await self.end_tournament(tournament_id)
        else:
            # Schedule next round
            asyncio.create_task(self.run_tournament_round(tournament_id))

    async def run_tournament_match(self, tournament_id: str, match_id: str):
        """Run a tournament match"""
        tournament = tournaments.get(tournament_id)
        if not tournament:
            return
        
        match = next((m for m in tournament["matches"] if m["id"] == match_id), None)
        if not match:
            return
        
        match["status"] = "running"
        
        # Simulate battle
        battle_id = f"battle_{uuid.uuid4().hex}"
        battle_data = {
            "id": battle_id,
            "player1": match["player1"],
            "player2": match["player2"],
            "start_time": datetime.utcnow(),
            "status": "active",
            "type": "tournament",
            "tournament_id": tournament_id,
            "match_id": match_id,
            "events": [],
            "winner": None
        }
        
        active_battles[battle_id] = battle_data
        
        # Simulate battle (simplified for tournaments)
        player1 = self.get_player_stats(match["player1"])
        player2 = self.get_player_stats(match["player2"])
        
        # Determine winner based on stats and random factor
        p1_score = player1["level"] * 10 + player1["damage"] + player1["armor"] + random.randint(-10, 10)
        p2_score = player2["level"] * 10 + player2["damage"] + player2["armor"] + random.randint(-10, 10)
        
        if p1_score > p2_score:
            winner = match["player1"]
        elif p2_score > p1_score:
            winner = match["player2"]
        else:
            winner = random.choice([match["player1"], match["player2"]])
        
        # Update match
        match["winner"] = winner
        match["status"] = "completed"
        battle_data["winner"] = winner
        battle_data["status"] = "completed"
        battle_data["end_time"] = datetime.utcnow()
        
        # Log event
        self.log_battle_event(
            battle_id,
            f"{self.get_player_name(winner)} wins the tournament match!"
        )
        
        # Clean up
        await asyncio.sleep(10)
        if battle_id in active_battles:
            del active_battles[battle_id]

    async def end_tournament(self, tournament_id: str):
        """Finalize a tournament and distribute prizes"""
        tournament = tournaments.get(tournament_id)
        if not tournament or tournament["status"] != "running":
            return
        
        tournament["status"] = "completed"
        tournament["end_time"] = datetime.utcnow()
        
        # Determine winner (last match winner)
        final_match = None
        for match in tournament["matches"]:
            if match["round"] == max(m["round"] for m in tournament["matches"]):
                final_match = match
                break
        
        if final_match and final_match["winner"]:
            winner_id = final_match["winner"]
            tournament["winner"] = winner_id
            
            # Award prizes (70% of prize pool to winner)
            prize = tournament["prize_pool"] * 0.7
            player_stats[winner_id]["credits"] += prize
            
            # Award runner-up (20% of prize pool)
            runner_up = final_match["player1"] if final_match["winner"] == final_match["player2"] else final_match["player2"]
            player_stats[runner_up]["credits"] += tournament["prize_pool"] * 0.2
            
            # Award organization (10%)
            # This would go to the game's revenue
            
            # Log event
            tournament_log = (
                f"Tournament '{tournament['name']}' completed!\n"
                f"Winner: {self.get_player_name(winner_id)} (Prize: {prize} credits)\n"
                f"Runner-up: {self.get_player_name(runner_up)}"
            )
            print(tournament_log)
        
        # Clean up after delay
        await asyncio.sleep(3600)  # Keep tournament data for 1 hour
        if tournament_id in tournaments:
            del tournaments[tournament_id]

    def join_tournament(self, player_id: str, tournament_id: str) -> dict:
        """Register a player for a tournament"""
        tournament = tournaments.get(tournament_id)
        if not tournament:
            return {"status": "error", "message": "Tournament not found"}
        
        if tournament["status"] != "scheduled":
            return {"status": "error", "message": "Tournament already started"}
        
        player = self.get_player_stats(player_id)
        
        # Check entry fee
        if player["credits"] < tournament["entry_fee"]:
            return {"status": "error", "message": "Insufficient credits"}
        
        # Deduct entry fee
        player["credits"] -= tournament["entry_fee"]
        tournament["participants"].append(player_id)
        
        return {"status": "success", "message": "Joined tournament"}

    def get_random_sponsor(self) -> str:
        """Get a random sponsor name"""
        sponsors = [
            "TechCorp", "Quantum Industries", "Nova Systems", "CyberDyne",
            "OmniCorp", "Apex Technologies", "FutureTech", "NeoArmaments"
        ]
        return random.choice(sponsors)

    def initialize_player(self, player_id: str):
        """Initialize a new player's stats"""
        player_stats[player_id] = {
            "id": player_id,
            "name": f"Player_{player_id[:6]}",
            "level": 1,
            "xp": 0,
            "credits": 100,
            "health": 100,
            "damage": 15,
            "armor": 10,
            "speed": 5,
            "skill_points": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "pve_wins": 0,
            "pve_losses": 0,
            "last_battle": None,
            "equipment": {},
            "battle_pass": {
                "active": False,
                "end_date": None,
                "level": 1,
                "xp": 0
            }
        }

    def get_player_stats(self, player_id: str) -> dict:
        """Get player stats, initializing if new"""
        if player_id not in player_stats:
            self.initialize_player(player_id)
        return player_stats[player_id]
    
    def get_player_name(self, player_id: str) -> str:
        """Get player name from stats"""
        if player_id.startswith("ai_"):
            ai = next((a for a in ai_players if a["id"] == player_id), None)
            return ai["name"] if ai else "AI Opponent"
        return player_stats.get(player_id, {}).get("name", "Unknown Player")

    def log_battle_event(self, battle_id: str, message: str):
        """Add an event to battle log"""
        battle = active_battles.get(battle_id)
        if battle:
            timestamp = datetime.utcnow().isoformat()
            battle["events"].append({
                "timestamp": timestamp,
                "message": message
            })
    
    def get_battle_status(self, battle_id: str) -> Optional[dict]:
        """Get current battle status"""
        return active_battles.get(battle_id)
    
    def get_player_battle(self, player_id: str) -> Optional[dict]:
        """Get active battle for a player"""
        for battle in active_battles.values():
            if battle["status"] == "active" and player_id in [battle["player1"], battle["player2"]]:
                return battle
        return None
    
    def upgrade_player_stat(self, player_id: str, stat: str) -> dict:
        """Upgrade a player's stat using skill points"""
        player = self.get_player_stats(player_id)
        
        if player["skill_points"] < 1:
            return {"status": "error", "message": "No skill points available"}
        
        valid_stats = ["health", "damage", "armor", "speed"]
        if stat not in valid_stats:
            return {"status": "error", "message": "Invalid stat"}
        
        # Apply upgrade
        upgrade_amount = 5 if stat == "health" else 1
        player[stat] += upgrade_amount
        player["skill_points"] -= 1
        
        return {"status": "success", "message": f"{stat.capitalize()} upgraded!"}

# Global game engine instance
game_engine = GameEngine()
