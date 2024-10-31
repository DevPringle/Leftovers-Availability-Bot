import discord
from discord.ext import commands
from discord.ui import Button, View, Select

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

availability_data = {}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIME_SLOTS = [
    "6:00-7:00",
    "7:00-8:00",
    "8:00-9:00",
    "9:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def availability(ctx):
    user_id = ctx.author.id

    if user_id not in availability_data:
        availability_data[user_id] = {day: [] for day in DAYS}

    day_select = Select(placeholder="Select a day...", options=[discord.SelectOption(label=day, value=day) for day in DAYS])
    view = View(timeout=None)
    view.add_item(day_select)

    async def day_selected(interaction: discord.Interaction):
        selected_day = interaction.data['values'][0]
        await interaction.response.edit_message(content=f"You selected **{selected_day}**. Now choose your time slots:", view=None)

        time_buttons_view = View()

        for slot in TIME_SLOTS:
            button = Button(label=slot, style=discord.ButtonStyle.secondary)

            async def toggle_time_slot(interaction: discord.Interaction, day=selected_day, time_slot=slot):
                if time_slot in availability_data[user_id][day]:
                    availability_data[user_id][day].remove(time_slot)
                    button.label = slot
                    button.style = discord.ButtonStyle.secondary
                else:
                    availability_data[user_id][day].append(time_slot)
                    button.label = f"{slot} (Selected)"
                    button.style = discord.ButtonStyle.success

                await interaction.response.edit_message(view=time_buttons_view)

            button.callback = toggle_time_slot
            time_buttons_view.add_item(button)

        submit_button = Button(label="Submit Availability", style=discord.ButtonStyle.green)

        async def submit_callback(interaction: discord.Interaction):
            await interaction.response.send_message(f"Your availability for **{selected_day}** has been recorded: {', '.join(availability_data[user_id][selected_day]) if availability_data[user_id][selected_day] else 'No slots selected.'}", ephemeral=True)
            print(availability_data)

        submit_button.callback = submit_callback
        time_buttons_view.add_item(submit_button)

        await ctx.send(content=f"You selected **{selected_day}**. Now choose your time slots:", view=time_buttons_view)

    day_select.callback = day_selected
    await ctx.send("Select a day for your availability:", view=view)

@bot.command()
async def report(ctx):
    report_message = "Availability Report:\n"
    for user_id, days in availability_data.items():
        user = ctx.guild.get_member(user_id)
        if user:
            report_message += f"**{user.name}**:\n"
            for day, times in days.items():
                report_message += f"  - {day}: {', '.join(times) if times else 'No slots selected.'}\n"
    await ctx.send(report_message)

bot.run('token')
