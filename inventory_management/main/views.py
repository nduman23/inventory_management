


# Standard library imports
import json
from datetime import date, datetime, time,timedelta
import logging

# Django importts for handling HTTP requests, user authetication, database operations, pagination and utilities
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.db.models import Q,Sum, F, Case, When, IntegerField
from django.utils.timezone import get_current_timezone, make_aware, now
from django.core.paginator import Paginator
from django.db import IntegrityError

# Imports from the current application modules
from main.models import *
from main.common import *

# Setup logger for this module
logger = logging.getLogger(__name__)

# Create your views here.

class HomePage(View):
    """
    A view for displaying the homepage of the stock management web application.
    
    It shows a limited number of categories and routers from the user's associated store, 
    ensuring that only items not marked as deleted are displayed. It also determines 
    if a 'show more' button should be displayed for categories and routers.
    """
    def get(self,req):
        """
        Handle GET request to render the homepage with specific categories and routers.
        
        Args:
            req: HttpRequest object representing the client's request.

        Returns:
            HttpResponse object that renders the homepage with the context data.
        """
        context = {}
        user = req.user # Get the logged-in user

        # Fetch up to 6 categories and routers from the user's store, excluding deleted items 
        categories = Category.objects.filter(store=user.store,deleted=False)[:6]
        routers = Router.objects.filter(store=user.store,deleted=False)[:6]

         # Determine if the 'show more' button should be displayed for categories and routers
        context['more_categories'] = len(categories) > 5
        context['more_routers'] = len(routers) > 5

        # Add the first 5 categories and routers to the context for rendering
        context['categories'] = categories[:5]
        context['routers'] = routers[:5]
        
        # Render the homepage template with the provided contex
        return render(req,'main/other/homepage.html',context=context)

class SignupView(View):
    """
    A view for handling new user registrations in the stock management web application.
    
    It supports rendering the signup form and processing form submissions to create new user accounts.
    """
    def get(self,req):
        """
        Handle GET request to show the signup form.
        
        Args:
            req: HttpRequest object representing the client's request.

        Returns:
            HttpResponse object that renders the signup form.
        """
        return render(req,'main/account/signup.html')
    
    def post(self,req):
        """
        Handle POST request to register a new user based on the form submission.
        
        Args:
            req: HttpRequest object representing the client's request.

        Returns:
            JsonResponse object indicating the success or failure of the user registration.
        """
        res = {'status':500,'message':'An error occured while processing the request'}
        try:
            body = json.loads(req.body) # Parse JSON data from the request body
            username = body.get('username')
            email = body.get('email')
            password1 = body.get('password1')
            password2 = body.get('password2')


            # Check for the presence of all required fields
            if not all([username,email,password1,password2]):
                res['message'] = 'All fields are required'
            # Validate password matching and length requirements    
            else:
                if password1 != password2:
                    res['message'] = 'Passwords do not match'
                elif len(password1) < 8:
                    res['message'] = 'The password is too short'
                    # Check for existing username or email to prevent duplicate
                elif username_or_email_exists(username,email):
                    res['message'] = 'Username or email already exists'
                else:
                    # Create and save the new user with the provided details
                    user = User.objects.create(username=username,email=email)
                    # Later use set_password method, this method will hash the password of the user instead of leaving it in plain text (For security)
                    user.set_password(password1)
                    user.save()
                    res['status'] = 200
                    del res['message']    # Remove error message on successful creation
        except Exception as e:
            logger.exception(e) # Log any exceptions for debugging
        return JsonResponse(res, status=res['status'])
    
class LoginView(View):
    """
    A view for handling user login in the stock management web application.
    
    It supports rendering the login form and processing form submissions for user authentication.
    """
    def get(self,req):
        """
        Handle GET request to show the login form.
        
        Args:
            req: HttpRequest object representing the client's request.

        Returns:
            HttpResponse object that renders the login form.
        """
        return render(req,'main/account/login.html')
    
    def post(self,req):
        """
        Handle POST request to authenticate a user based on the login form submission.
        
        Args:
            req: HttpRequest object representing the client's request.

        Returns:
            JsonResponse object indicating the success or failure of the login attempt.
        """
        res = {'status':500,'message':'An error occured while processing the request'}
        try:
            body = json.loads(req.body) # Parse JSON data from request body
            username = body.get('username')
            password = body.get('password')
            if username and password:
                 # Attempt to authenticate the user with provided credentials
                user = authenticate(req, username = username, password=password)
                if not user:
                    # Attempt to authenticate using email if username fails
                    email_user = User.objects.filter(email = username).first()
                    if email_user:
                        user = authenticate(req, username = email_user.username, password=password)
                if user:
                     # If authentication is successful, log the user in
                    login(req, user)
                    res['status'] = 200
                    del res['message']  # Remove error message on successful login
                else:
                    # Handle invalid username/email or password
                    matched_user = User.objects.filter(Q(username = username) | Q(email = username))
                    if not matched_user:
                        res['message'] = ('Invalid username or email')
                    elif not matched_user[0].check_password(password):
                        res['message'] = ('Invalid password')
        except Exception as e:
            logger.exception(e) # Log any exceptions for debugging
        return JsonResponse(res, status=res['status'])
    

class ProfileView(View):
    """
    A view for displaying and managing user profiles in the stock management web application.
    
    Supports displaying the profile page, updating user information, managing alert threshold settings for a store,
    and removing users from a store. Different HTTP methods (GET, POST, PUT, DELETE) are used to handle
    the respective operations.
    """
    def get(self,req):
        """
        Handles GET requests to display the user's profile page, including a list of other users associated with the same store.
        
        Args:
            req: HttpRequest object representing the client's request.
            
        Returns:
            HttpResponse object that renders the profile page with context data including store users.
        """
        context = {}
        user = req.user # The current logged-in user

        # Fetch all users associated with the same store as the logged-in user, excluding the user themselves
        store_users = list(req.user.store.user_set.all().exclude(id=user.id).values())
        context['store_users'] = store_users # Add the store users to the context 

        # Render the profile page with the provided context
        return render(req,'main/account/profile.html',context=context)
    
    def post(self,req):
        """
        Handles POST requests to update information about a user, such as their role within the store.
        This operation is restricted to users with the 'store_manager' role.
        
        Args:
            req: HttpRequest object representing the client's request.
            
        Returns:
            JsonResponse object indicating the success or failure of the update operation.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            # Authorization check: proceed only if the user has a 'store_manager' role
            if req.user.role != "store_manager":
                res['status'] = 403
                res['message'] = "You don't have enough permissions"
                return JsonResponse(res,status=res['status'])
            
            store = req.user.store  # The store associated with the logged-in user
            body = json.loads(req.body)  # Parse the request body to get the data
            username = body.get('username')  # Username or email of the user to update
            role = body.get('role')  # New role to assign

            # Try fo find the user by username or email
            added_user = User.objects.filter(Q(username=username) | Q(email=username)).first()
            if added_user:
                # Update the user's store and role accordingly if found
                if added_user.store == store :
                    added_user.role = role
                    message = 'edited'
                else:
                    added_user.store = store
                    added_user.role = role
                    message = 'added'
                added_user.save()
                res['status'] = 200
                res['message'] = f'User {message} successfully'
            else :
                res['message'] = 'User not found'
        except Exception as e:
            logger.exception(e) # Log any exception for debugging
        return JsonResponse(res,status=res['status'])

    def put(self,req):
        """
        Handles PUT requests to update the alert threshold setting for the store associated with the logged-in user.
        
        Args:
            req: HttpRequest object representing the client's request.
            
        Returns:
            JsonResponse object indicating the success or failure of the operation to update the alert threshold.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            body = json.loads(req.body) # Parse the request body to extract the new value
            value = body.get('value')   # New alert threshold value
            if value:
                store = req.user.store  # The store associated with the logged-in user
                store.alert_on = value  # Update the alert threshold
                store.save()
                res['status'] = 200
                res['message'] = 'Alert threshold edited successfully'
        except Exception as e:
            logger.exception(e) # Log any exception for debugging
        return JsonResponse(res,status=res['status'])
    
    def delete(self,req):
        """
        Handles DELETE requests to remove a user from the store. This operation is restricted to users with the 'store_manager' role.
        
        Args:
            req: HttpRequest object representing the client's request.
            
        Returns:
            JsonResponse object indicating the success or failure of the operation to remove a user.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            # Authorization check: proceed only if the user has a store_manager role
            if req.user.role != "store_manager":
                res['status'] = 403
                res['message'] = "You don't have enough permissions"
                return JsonResponse(res,status=res['status'])
            
            body = json.loads(req.body) # Parse the request body to get the user ID
            user_id = body.get('id')    # ID of the user to remove
            
           # Attempt to find the user by ID
            store_user = User.objects.filter(id=user_id).first()
            if store_user:
                # Remove the user from the store and clear their role
                store_user.role = None
                store_user.store = None
                store_user.save()
                res['status'] = 200
                res['message'] = 'User deleted successfully'
            else:
                res['message'] = "Can't find the user"
        except Exception as e:
            logger.exception(e)  # Log any exception for debugging
        return JsonResponse(res,status=res['status'])

        
class DashboardView(View):
    """
    A view for displaying the dashboard page within the stock management web application.
    
    This dashboard includes various statistics and listings for the user's store, such as routers, categories, 
    employee actions, and monitoring stats. It is designed to give an overview of the store's status 
    and activity, including trend analysis over the last five days.
    """
    def get(self,req):
        """
        Handles GET requests to render the dashboard with various statistics and information related to the user's store.
        
        Args:
            req: HttpRequest object representing the client's request.
            
        Returns:
            HttpResponse object that renders the dashboard page with context data.
        """
        user = req.user
        store = user.store
        query = req.GET # Query parameters from the request
        context = {}


        # Color scheme for graphical elements in the dashboard
        colors = ["#e58989","#edcb8d","#6868e5"]

        # Calculate the last 5 days for trend analysis
        days = list(reversed([today_midnight() - timedelta(days=x) for x in range(5)]))
        
        # Routers Section: Processing routers with optional filtering based on query parameters
        router_page = query.get('router_page') if query.get('router_page') else 1
        routers = Router.objects.filter(store=user.store,deleted=False).order_by('-id')

        # Apply filters based on query parameters for routers 
        emei = query.get('emei')
        serial = query.get('serial')
        category = query.get('router_category')
        router_type = query.get('router_type')
        status = query.get('status')
        if emei:
            routers = routers.filter(emei__icontains=emei)
        if serial:
            routers = routers.filter(serial_number__icontains=serial)
        if router_type:
            routers = routers.filter(category__type=router_type)
        if category:
            category_instance = Category.objects.filter(id=category).first()
            if category_instance:
                routers = routers.filter(category=category_instance)
        if status:
            routers = routers.filter(status=status)
        
        # Pagination for routers listing
        router_paginator = Paginator(routers,10)
        routers = router_paginator.page(router_page)
        context['statuses'] = Router.STATUSES
        context['routers_count'] = router_paginator.count
        context['routers_paginator'] = router_paginator.get_elided_page_range(number=router_page, 
                                           on_each_side=1,
                                           on_ends=1)
        
       # Categories Section: Similar processing for categories with pagination
        categories_page = query.get('categories_page') if query.get('categories_page') else 1
        categories = Category.objects.filter(store=user.store,deleted=False).order_by('-id')
        category_name = query.get('category_name')
        category_type = query.get('category_type')
        if category_name:
            categories = categories.filter(name__icontains=category_name)
        if category_type:
            categories = categories.filter(type=category_type)

        category_paginator = Paginator(categories,10)
        categories = category_paginator.page(categories_page)
        context['categories_paginator'] = category_paginator.get_elided_page_range(number=categories_page, 
                                           on_each_side=1,
                                           on_ends=1)
        

        # Employees Section: Compile actions taken by employees on routers over the last 5 days
        employees = User.objects.filter(store=store)
        actions = ['add','edit','delete']
        for action in actions:
            context[action] =  {}
            for emp_index,employee in enumerate(employees):
                obj = []
                for day_index,day in enumerate(days):
                    date_start = make_aware(day)
                    date_end = make_aware(day + timedelta(days=1))
                    logs = Log.objects.filter(store=store,user=employee,action=action,instance="router",created_at__gte=date_start,created_at__lt=date_end).count()
                    if logs:
                        obj.append(logs)
                    else:
                        obj.append(0)
                color = colors[emp_index % len(colors)]
                context[action][employee.username] = {'obj':obj,'color':color+'33','border':color}

        # Monitors Section: Display routers by category and overall store performance
        # Routers per category and overall store monitors are compiled here
        # This section includes complex logic for aggregating and presenting monitoring data
        # (The detailed comments for this section are omitted for brevity but follow a similar pattern to the above sections)
        
        # Update the context with additional data for rendering in the template
        context['monitors'] = []
        store_monitors = []

        #Routers per category section
        routers_categories = Category.objects.filter(store=store,deleted=False)

        # Iterate over each category in the routers_categories list with its index
        for index,category in enumerate(routers_categories):
            # Initialize an empty list to hold the data for the current category
            obj = []

            # Iterate over each day in the days list with its index
            for day_index,day in enumerate(days):
                # Special case for the fifth day (index 4, since indexing starts at 0)
                if day_index == 4:
                    obj.append(category.count_routers())
                else:
                    date_start = day
                    date_end = day + timedelta(days=1)
                    monitoring = Monitoring.objects.filter(store=store,category=category,day__gte=date_start,day__lt=date_end).first()
                    if monitoring:
                        obj.append(monitoring.routers)
                    else:
                        default = 0
                        if day_index > 0:
                            default = obj[day_index - 1]
                        obj.append(default)
            color = colors[index % len(colors)]
            monitor_obj = {'label':category.name,'values':obj,'color':color+'33','border':color}
            
            context['monitors'].append(monitor_obj)
        
        #Routers by store section
        for day_index,day in enumerate(days):
            if day_index == 4:
                store_monitors.append(store.count_routers())
            else:
                date_start = day
                date_end = day + timedelta(days=1)
                condition1 = Q(store=store)
                condition2 = Q(day__gte=date_start)
                condition3 = Q(day__lt=date_end)

                condition = Case(
                    When(condition1 & condition2 & condition3, then=F('routers')),
                    default=0,
                    output_field=IntegerField()
                )
                result = Monitoring.objects.aggregate(total=Sum(condition))
                total = result.get('total')
                # When there is no entry for this date, and index > 1, keep the same amount of routers of yesterday for today
                if not total and day_index > 0 and not Monitoring.objects.filter(store=store,day__gte=date_start,day__lt=date_end):
                    total = store_monitors[day_index - 1]

                    
                store_monitors.append(total)

        context['stores'] = Store.objects.all()
        context['routers'] = routers
        context['categories_obj'] = categories
        context['categories'] = routers_categories
        context['action'] = actions
        context['store_monitors'] = store_monitors    
        context['days'] = [day.strftime("%A") for day in days]
        return render(req,'main/dashboard/index.html',context=context)
    

class CreateStoreView(View):
    """
    Handles the creation of new stores. Supports displaying the store creation form via GET request
    and processing the form submission (store creation) via POST request.
    """
    def get(self,req):
        """
        Renders the store creation form.
        """
        # Directly renders the template for creating a new store
        return render(req,'main/store/create-store.html')
    

    def post(self,req):
        """
        Processes the POST request to create a new store based on the provided name.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            # We format the body of the request to a Python dictionary
            body = json.loads(req.body)
            # We retrieve the name from the body of the request
            name = body.get("name")
            #Create the store and save it to the database
            store = Store.objects.create(name=name)
            store.save()
            # Associate the created store to the user and assign him as the store manager
            user = req.user
            user.store = store
            user.role = 'store_manager'
            user.save()
            res['status'] = 200
            del res['message'] # Remove the error message on success
        except Exception as e:
            logger.exception(e) # Log the exception for debugging purposes
        return JsonResponse(res,status=res['status'])

class CreateCategoryView(View):
    """
    View for creating a new category within a store.
    Handles GET requests to display the category creation form and POST requests to create a category.
    """
    def get(self,req):
        """
        Renders the category creation form.
        """
        return render(req,'main/category/create-category.html')
    

    def post(self,req):
        """
        Creates a new category based on the details provided in the POST request.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            if req.user.role != "store_manager":
                res['status'] = 403
                res['message'] = "You don't have enough permissions"
                return JsonResponse(res,status=res['status'])
            user = req.user
            store = user.store
            # We format the body of the request to a Python dictionary
            body = json.loads(req.body)
            # We retrieve the name and type from the body of the request
            name = body.get("name")
            category_type = body.get('type')
            # Create the Category instance and save it to the database
            category = Category.objects.create(name=name,type=category_type,store=store)
            category.save()
            # Log the creation action
            Log.objects.create(user = user,store = store,instance='category',instance_id=category.id,category_name=category.name,action='add')

            res['status'] = 200
            del res['message'] # Remove the error message on success
        except Exception as e:
            logger.exception(e) # Log the exception for debugging purposes
        return JsonResponse(res,status=res['status'])
    
    
class CreateRouterView(View):
    """
    Facilitates creating new routers within a store. It renders a router creation form for GET requests
    and handles router creation with POST requests.
    """
    def get(self,req):
        """
        Displays the router creation form along with the available categories.
        """
        context = {}
        store = req.user.store
        # Fetch categories that are not marked as deleted and belong to the user's store
        categories = list(Category.objects.filter(store=store,deleted=False).values())
        context['categories'] = categories
        return render(req,'main/router/create-router.html',context=context)
    

    def post(self,req):
        """
        Processes the POST request to create a new router based on the provided details.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            if req.user.role != "store_manager":
                res['status'] = 403
                res['message'] = "You don't have permissions"
                return JsonResponse(res,status=res['status'])
            

            user = req.user
            store = user.store
            #We format the body of the request to a python object
            body = json.loads(req.body)
            #We retrieve the name from the body of the request
            category = body.get('category')
            serial_number = body.get('serial_number')
            

            # Validate and fetch the category
            category = Category.objects.filter(id=category).first()
            # Create the router instance and save it to the database
            router = Router.objects.create(store=store,category=category,serial_number=serial_number)
            router.save()
            # Reset the alerted flag for the category as a new router is adde
            category.alerted = False
            category.save()
            # Log the router addition
            Log.objects.create(user = user,store = store,instance='router',instance_id=router.id,serial_number=router.serial_number,action='add')

            res['status'] = 200
            del res['message']

        except IntegrityError :
            res['message'] = 'Router already exists in the database'
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])
    

class CreateRoutersView(View):
    """
    A view that supports the bulk creation of routers within a store. It provides functionality to render
    a bulk router creation form and to process submissions of this form for creating multiple routers at once.
    """
    def get(self,req):
        """
        Renders the bulk routers creation form along with available categories.
        """
        context = {}
        store = req.user.store
        # Fetch categories that are not marked as deleted and belong to the user's store
        categories = list(Category.objects.filter(store=store,deleted=False).values())
        context['categories'] = categories
        return render(req,'main/router/bulk-create.html',context=context)
    
    def post(self,req):
        """
        Processes the POST request to create multiple routers based on the provided serial numbers and category.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            if req.user.role != "store_manager":
                res['status'] = 403
                res['message'] = "You don't have permissions"
                return JsonResponse(res,status=res['status'])
            
            user = req.user
            store = user.store
            #We format the body of the request to a python object
            body = json.loads(req.body)
            #We retrieve the name from the body of the request
            serial_numbers = body.get('serial_numbers')
            logger.info(f'{len(serial_numbers)} serial numbers received')
            category = body.get('category')

            # Validate and fetch the category
            category = Category.objects.filter(id=category).first()
            for sn in serial_numbers:
                try:
                    router = Router.objects.create(store=store,category=category,serial_number=sn)
                    router.save()
                    Log.objects.create(user = user,store = store,instance='router',instance_id=router.id,serial_number=router.serial_number,action='add')
                except Exception as e:
                    logger.exception(e)

            category.alerted = False
            category.save()
            # Log the router addition

            res['status'] = 200
            del res['message']
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])


class CategoryView(View):
    """
    Provides functionality for editing and deleting categories. This view handles PUT requests to edit category
    details and DELETE requests to mark categories as deleted within the user's store.
    """
    def put(self,req):
        """
        Edits an existing category's details based on the provided information in the request body.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            if req.user.role != "store_manager":
                res['status'] = 403
                res['message'] = "You don't have enough permissions"
                return JsonResponse(res,status=res['status'])
            
            body = json.loads(req.body)
            category_id = body.get('id')
            name = body.get('name')
            category_type = body.get('type')

            category = Category.objects.filter(store = req.user.store,id=category_id).first()
            if category:
                category.name = name
                category.type = category_type
                category.save()
                # Log the category edit action
                Log.objects.create(user = req.user,store = req.user.store,instance='category',instance_id=category.id,category_name=category.name,action='edit')
                res['status'] = 200
                res['message'] = 'Category edited successfully'

        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])
    
    def delete(self,req):
        """
        Marks an existing category as deleted based on the category ID provided in the request body.
        """
        res = {"status":500,"message":"Something wrong hapenned"}
        try:
            if req.user.role != "store_manager":
                res['status'] = 403
                res['message'] = "You don't have enough permissions"
                return JsonResponse(res,status=res['status'])
            body = json.loads(req.body)
            category_id = body.get('id')
            category = Category.objects.filter(store = req.user.store, id=category_id).first()
            if category:
                category.deleted = True
                category.save()
                # Log the category deletion
                Log.objects.create(user = req.user,store = req.user.store,instance='category',instance_id=category.id,category_name=category.name,action='delete')
                res['message'] = 'Category deleted successfully'
                res['status'] = 200
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])

    

class RouterView(View):
    """
    A view dedicated to managing routers within a user's store. It supports operations such as listing routers,
    importing multiple routers, editing router details, marking routers as deleted, and updating the shipment status
    of routers.
    """
    def get(self,req):
        """
        Retrieves and lists all routers associated with the user's store, excluding those marked as deleted.
        """
        res = {"status":500,"message":"Something wrong hapenned"}
        try:
            user = req.user
            store = user.store
            # Fetch routers from the store, ordered by descending ID
            routers = list(Router.objects.filter(store=store).order_by("-id").values('id','category__name','emei','serial_number','created_at'))
            res['routers'] = routers
            del res['message']
            res['status'] = 200
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])
    
    def post(self,req):
        """
        Imports a batch of routers from a provided list, creating new router entries in the database.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            user = req.user
            body = json.loads(req.body)
            routers = body.get('routers')
            imported = 0 # Counter for successfully imported routers
            for new_router in routers:
                try:
                    category = Category.objects.filter(name=new_router.get('category')).first()
                    if category:
                        # Check if the router does not exist or is marked as deleted
                        if not Router.objects.filter(id=new_router.get('id')).exists():
                            if category:
                                router = Router.objects.create(store = user.store,category=category,emei=new_router.get('emei'),serial_number=new_router.get('serial_number'))
                                router.save()
                                Log.objects.create(user = user,store = user.store,instance='router',instance_id=router.id,serial_number=router.serial_number,action='add')
                                imported += 1

                        elif Router.objects.filter(id=new_router.get('id'),deleted=True).exists():
                                router = Router.objects.get(id=new_router.get('id'))
                                router.category = category
                                router.emei=new_router.get('emei')
                                router.serial_number=new_router.get('serial_number')
                                router.deleted = False
                                router.save()
                                Log.objects.create(user = user,store = user.store,instance='router',instance_id=router.id,serial_number=router.serial_number,action='add')
                                imported += 1
                    else:
                        logger.error(f"{new_router.get('category')} not found")
                                

                except Exception as e:
                    logger.exception(e)
            res['status'] = 200
            res['message'] = f'{imported} routers imported'
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])

    def put(self,req):
        """
        Edits the details of an existing router based on the provided ID and details.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            if req.user.role != "store_manager":
                res['status'] = 403
                res['message'] = "You don't have enough permissions"
                return JsonResponse(res,status=res['status'])
            body = json.loads(req.body)
            router_id = body.get('id')
            category = body.get('category')
            serial_number = body.get('serial_number')
            emei = body.get('emei')
            status = body.get('status')
            
            category_instance = Category.objects.filter(id=category).first()
            router = Router.objects.filter(store = req.user.store,id=router_id).first()
            router.category = category_instance
            router.serial_number = serial_number
            router.emei = emei
            router.status = status
            router.save()
            Log.objects.create(user = req.user,store = req.user.store,instance='router',instance_id=router.id,serial_number=router.serial_number,action='edit')
            res['status'] = 200
            res['message'] = 'Router edited successfully'

        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])
    
    def delete(self,req):
        """
        Marks an existing router as deleted based on the provided ID.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            if req.user.role != "store_manager":
                res['status'] = 403
                res['message'] = "You don't have enough permissions"
                return JsonResponse(res,status=res['status'])
            body = json.loads(req.body)
            router_id = body.get('id')
            router = Router.objects.filter(store = req.user.store, id=router_id).first()
            if router:
                router.deleted = True
                router.save()
                Log.objects.create(user = req.user,store = req.user.store,instance='router',instance_id=router.id,serial_number=router.serial_number,action='delete')
                logger.info(f'{req.user.username} deleted router with sn: {router.serial_number} - emei : {router.emei}')
                res['message'] = 'Router deleted successfully'
                res['status'] = 200
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])
    
    def patch(self,req):
        """
        Toggles the shipment status of a router based on the provided ID.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try:
            body = json.loads(req.body)
            router_id = body.get('id')
            if router_id:
                router = Router.objects.filter(store=req.user.store,id=router_id).first()
                if router:
                    router.shipped = not router.shipped
                    router.save()
                    res['message'] = 'Router shipment status updated successfully'
                    res['status'] = 200
                else:
                    res['message'] = 'Router not found'
                    res['status'] = 400

        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])



class RouterSuggestions(View):
    """
    Provides autocomplete suggestions for router serial numbers based on partial input.
    """
    def get(self,req):
        """
        Retrieves a list of routers that match the partial EMEI or serial number provided by the user.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try :
            user = req.user
            value = req.GET.get('value')
            # Filter routers by store, not deleted, and starting with the given value
            routers = list(Router.objects.filter(Q(store = user.store) & Q(deleted = False) & (Q(emei__startswith=value) | Q(serial_number__startswith=value))).values('emei'))
            res['status'] = 200
            res['routers'] = routers
            del res['message']
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])
    
    
class CategorySuggestions(View):
    """
    Provides autocomplete suggestions for category names based on partial input.
    """


    def get(self,req):
        """
        Retrieves a list of categories matching the partial name input provided by the user.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try :
            user = req.user
            value = req.GET.get('value')
            # Filter categories by store, name starting with the given value, and not deleted
            categories = list(Category.objects.filter(store = user.store ,name__startswith=value,deleted=False).values('name'))
            res['status'] = 200
            res['categories'] = categories
            del res['message']
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])
    
class LogsView(View):
    """
    Manages the display of logs and actions for items within the user's store, including support for filtering
    and pagination to enhance usability.
    """
    model = Log
    paginate_by = 20
    template_name = "main/logs/list.html"

    def get(self,request):
        """
        Fetches and displays logs and actions based on applied filters and pagination settings.
        """
        user = request.user
        logs = Log.objects.filter(store=user.store).order_by('-id')
        actions = Action.objects.filter(store=user.store).order_by('-id')
        context = {}
        query = self.request.GET
        context['users'] = User.objects.filter(Q(store = request.user.store) | Q(is_superuser = True))
        try:
            logs_page = query.get('logs_page') if query.get('logs_page') else 1
            emei = query.get('emei')
            searched_user = query.get('user')
            action = query.get('action')
            instance = query.get('instance')
            if emei:
                logs = logs.filter(Q(emei__icontains=emei) | Q(category_name__icontains=emei))
            if searched_user:
                searched_user_instance = User.objects.filter(store=user.store, id=searched_user).first()
                if searched_user:
                    logs = logs.filter(user = searched_user_instance)
                else:
                    logs = logs.none()
            if action:
                logs = logs.filter(action=action)
            if instance:
                logs = logs.filter(instance=instance)
            logs_paginator = Paginator(logs,10)
            logs = logs_paginator.page(logs_page)
            context['logs'] = logs
            context['logs_obj'] = logs_paginator.get_elided_page_range(number=logs_page, 
                                            on_each_side=1,
                                            on_ends=1)
            
        except Exception as e:
            logger.exception(e)

        try:
            actions_page = query.get('actions_page') if query.get('actions_page') else 1
            router1 = query.get('action_router1')
            action = query.get('action_action')
            action_reason =  query.get('action_reason')
            searched_user = query.get('action_user')


            if router1:
                actions = actions.filter(router1=Router.objects.filter(emei=router1).first())
            
            if searched_user:
                searched_user_instance = User.objects.filter(store=user.store, id=searched_user).first()
                if searched_user:
                    actions = actions.filter(user = searched_user_instance)
                else:
                    actions = actions.none()
            
            if action:
                actions = actions.filter(action=action)
            
            if action_reason:
                actions = actions.filter(reason=action_reason)

            actions_paginator = Paginator(actions,10)
            actions = actions_paginator.page(actions_page)
            context['actions'] = actions
            context['actions_obj'] = actions_paginator.get_elided_page_range(number=actions_page, 
                                            on_each_side=1,
                                            on_ends=1)
            
        except Exception as e:
            logger.exception(e)

        return render(request,'main/logs/list.html',context=context)
    
class LogsOpsView(View):
    """
    Provides an API endpoint for retrieving logs associated with the user's store, with support for ordering and
    potentially filtering the logs.
    """
    
    # Assuming the rest of the method implementation follows the provided structure,
    # focusing on fetching logs and actions, applying filters, and paginating results.
    def get(self,req):
        """
        Returns a list of logs associated with the user's store.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        try :
            logs = list(Log.objects.filter(store = req.user.store).order_by('-id').values('user__username','action','instance','serial_number','category_name','instance_id','created_at'))
            res['logs'] = logs
            res['status'] = 200
            del res['message']
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])
    
class ActionsView(View):
    """
    Manages router actions such as returns, swaps, and updates on shipped status. It supports operations to create new actions
    and change the shipped status of an existing action.
    """
    def get(self,req):
        """
        Renders the main page for router actions, providing UI for initiating new actions or modifying existing ones.
        """
        # This method simply renders the main actions page without any dynamic context
        return render(req,'main/actions/main.html')
    
    def post(self,req):
        """
        Processes a request to create a new action on a router. It supports various action types including returns, swaps,
        collections, and sales, each with its own specific logic and validation.
        """
        res = {"status":500,"message":"An errror occured while processing the request"}
        # Implementation as provided, handling different action types and updating routers accordingly.

        try :
            store = req.user.store
            body = json.loads(req.body)
            action_type = body.get('action')
            sn1 = body.get('sn1')
            sn2 = body.get('sn2')
            order_number = body.get('order_number')
            router1 = Router.objects.filter(store=store,serial_number=sn1).first()
            router2 = None
            
            if not router1:
                if action_type == 'return' or action_type == 'swap':
                    #Check collected routers from other stores
                    router1, created = Router.objects.get_or_create(serial_number=sn1)
                    if created:
                        router1.store = store
                    
                     
            if not router1:
                res['message'] = "We can't find the router with the provided details"
                return JsonResponse(res,status=res['status'])
            if sn2:
                router2, created = Router.objects.get_or_create(serial_number=sn2)
                if created:
                    router2.store=store
            
            if router1:
                reason = None
                action_router_2 = None
                action_order_number = None
                if action_type == 'return':
                    #Check if routers is collected or swapped
                    # if not router1.status == Router.STATUSES[2][0] and not router1.status == Router.STATUSES[4][0]: #collected or device swap
                    #     res["message"]="This router is not collected."
                    #     return JsonResponse(res,status=res['status'])
                    reason = body.get('return_reason')
                    router1.status = Router.STATUSES[3][0]#return
                    router1.reason = body.get('return_reason')
                    emails = list(store.user_set.filter(role=User.Roles[0][0]).values_list('email',flat=True))
                    text = f"""Router with Serial number {router1.serial_number} was returned
reason: {router1.reason}
comment: {body.get('comment')}
{f"note: router was collected from {router1.store}" if router1.store == store else ""}
                            """
                    router1.store = store
                    send_email(emails,'Router Returned',text)
                elif action_type == 'swap':
                    # if not router1.status == Router.STATUSES[2][0]:  #collected
                    #     res["message"]="The router returned is not collected."
                    #     return JsonResponse(res,status=res['status'])
                    # if not router2.status == Router.STATUSES[0][0]: #in stock
                    #     res["message"]="This new collected router is not in stock."
                    #     return JsonResponse(res,status=res['status'])
                    reason = body.get('swap_reason')
                    action_router_2 = router2
                    router1.status = Router.STATUSES[2][0] #collected
                    router2.status = Router.STATUSES[4][0] #swap
                    router2.reason = body.get('return_reason')
                    emails = list(store.user_set.filter(role=User.Roles[0][0]).values_list('email',flat=True))
                    text = f"""Router with Serial number {router1.serial_number} was swapped with {router2.serial_number}
reason: {router1.reason}
comment: {body.get('comment')}
{f"note: router was collected from {router1.store}" if router1.store == store else ""}
"""
                    router1.store = store
                    send_email(emails,'Router Returned',text)
                elif action_type == 'collect':
                    if not router1.status == Router.STATUSES[1][0] and not router1.status == Router.STATUSES[0][0]: #Sold or in stock
                        if router1.status == Router.STATUSES[2][0]:
                            res["message"]="This router is already collected."
                        else:
                            res["message"]="This router is not sold."
                        return JsonResponse(res,status=res['status'])
                    router1.status = Router.STATUSES[2][0]
                    action_order_number = order_number
                elif action_type == 'sale':
                    if not router1.status == Router.STATUSES[0][0]: #In stock
                        if router1.status == Router.STATUSES[1][0]: #Sold
                            res["message"]="This router is already sold."
                        elif router1.status == Router.STATUSES[2][0]:#collected
                            res["message"]="This router is already collected."
                        else:
                            res["message"]="This router is not in stock."
                        return JsonResponse(res,status=res['status'])
                    router1.status = Router.STATUSES[1][0]
                    action_order_number = order_number
                    emails = list(store.user_set.all().values_list('email',flat=True))
                    text = f"Router with Serial number {router1.serial_number} was sold"
                    send_email(emails,'New sale',text)
                
                action = Action.objects.create(user = req.user,store=req.user.store,router=router1,action=action_type,comment=body.get('comment'),router2=action_router_2,reason=reason,order_number=action_order_number)
                action.save()
                router1.save()
                if router2:router2.save()

                res['status'] = 200
                del res['message']
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])
    
    def put(self,req):
        """
        Toggles the shipped status of an action based on its ID. This method allows updating an action's status to reflect
        its current shipping state.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        # Implementation as provided, toggling the shipped status of a specified action.
        try:
            if not req.user.role == "store_manager":
                res['message'] = "You don't have enough permissions"
                return JsonResponse(res,status=res['status'])
            body = json.loads(req.body)
            
            action_id = body.get('id')
            action =  Action.objects.filter(id=action_id,store = req.user.store).first()
            if action:
                action.shipped = False if action.shipped else True
                action.save()
                res['status'] = 200
                res['message'] = 'Action edited successfully'
            else:
                res['message'] = 'Action not found'
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])

class ReturnView(View):
    """
    Dedicated to handling returned routers. It provides a view that lists all routers marked as returned within the user's store,
    supporting pagination for efficient navigation through the list.
    """
    def get(self,req):
        """
        Fetches and displays routers marked as returned, applying pagination to the result set for manageable browsing.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        # Implementation as provided, reassigning the specified router to a new store if both entities are found to be valid.
        context = {}
        try:
            routers_page = req.GET.get('router_page') if req.GET.get('router_page') else 1 
            routers  = Router.objects.filter(store=req.user.store,status="return")
            context['categories'] = Category.objects.filter(store=req.user.store,deleted=False)
            context['routers_count'] = routers.count()
            routers_ordered = routers.order_by('-created_at')
            routers_paginator = Paginator(routers_ordered,10)
            routers = routers_paginator.page(routers_page)
            context['routers_paginator'] = routers_paginator
            context['routers'] = routers
            context['routers_obj'] = routers_paginator.get_elided_page_range(number=routers_page, 
                                            on_each_side=1,
                                            on_ends=1)
        except Exception as e:
            logger.exception(e)
        return render(req,'main/return/index.html',context=context)


class SwitchStore(View):
    """
    Facilitates the process of switching a router's assigned store to a new store as specified in the request. This action allows
    for dynamic management of router inventory across different store locations.
    """
    def post(self,req):
        """
        Handles the request to change a router's associated store to a new store specified by the user. It ensures that both the
        router and the new store exist before proceeding with the update.
        """
        res = {"status":500,"message":"An error occured while processing the request"}
        # Implementation as provided, reassigning the specified router to a new store if both entities are found to be valid.
        try:
            body = json.loads(req.body)
            router_id = body.get('router_id')
            new_store = body.get('new_store')
            router = Router.objects.filter(id=router_id).first()
            store = Store.objects.filter(id=new_store).first()
            if router and store:
                router.store = store
                router.save()
                res['status'] = 200
                res['message'] = "Store switched successfully"
            elif router:
                res['message'] = "Store not found"
            else:
                res['message'] = "Router not found"
                
        except Exception as e:
            logger.exception(e)
        return JsonResponse(res,status=res['status'])

