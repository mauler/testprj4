
# Cards Issuer Project


## Setup

This project runs over python **3.6** version.

This section doesn't cover environment setup. Just make sure the **python3.6** command is available on your path and the *dependencies are installed*.


### Installing dependencies

The dependencies are split in production and development. Install the development depencies using the command:

    python3.6 -m pip install -r requirements/development.txt

This will install the production dependencies and plus the development packages such as *pytest* and other tools.


### Testing

You can execute the project tests available on **tests/** folder by invoking Makefile command *test*:

    make test

This command invokes **pytest** that will discover tests around the project working folder, execute them and should the code coverage.

**ATTENTION**: Make sure the dependencies are installed.


### Running


    make run

This command invokes **migrate** followed by **runserver** django command.

## Code Architecture

All the code architecture focus in making the code life cycle easier by splitting components to ensure each has it responsibility and business rules strictly declared. This also helps the development focused on unit testing each of them.


### Package namespacing

| Package               | Description                                        |
|-----------------------|----------------------------------------------------|
| **cards.accounting**  | Django application for accounting.                 |
| **cards.api**         | The Endpoints views.                               |
| **cards.issuer**      | Issuer service persistence implemenation.          |
| **issuer.service**    | The issuer service operations used by the Scheme.  |
| **issuer.db**         | Abstract class for issuer persistence.             |


### Issuer Service

Available at **issuer/service.py** it's a *bridge* class responsible to implement the business rules related to the *webhook* used by the **Scheme**.

It wraps  the database calls:
1. Normalizing the return values (and exceptions)
2. Logging stuff
3. Doing minor parameters validation.


### Database Layer

The database layer is composed by the calls made by the issuer service plus the accounting business rules to make these calls work.

The issuer service implementation necessary is declared at **issuer/db.py** file over the abstract class **IssuerDatabase**.

The implementation is done by  **CardsIssuerDatabase** at **cards/issuer.py**, making sure the calls are properly encapsulated to raise the properly exceptions if an error occurs. This implementation also encapsulate *accounting operations* such as:

 - Funds transfer around accouts
 - Presentment settlement operation: debit and credit (Issuer and Scheme split).

#### The Database Schema

There are 2 contexts implemented:

- Accouting
- Cards

There is an ambiguous *thing* related to **CARD_ID**.  On the accouting context makes more sense to call it **ACCOUNT_OWNER** since for example the Issuer and the Scheme doesn't have cards but still have accounts ("balance on some currency").

This application is a **ALPHA PROTOTYPE** so the concepts may be a little inconsistent.

##### Entities definition:

Some entities have similar responsibilities and naming convention, the project follows this approach:

| Entity      | Description                                                              |
|-------------|--------------------------------------------------------------------------|
| Transaction | Used for cards transactions, not related to accounting.                  |
| Batch       | Is the real accounting transaction, *transfers* are know as **Journal**. |


### Django components

At this project *Django* is being used for 2 different things:

1. Endpoints serving (views).
2. Database abstraction (models).

It's important to say that the parts are *"easily"* plug-able. Easily meaning *possible* not *without work*.

They *don't relay* in each other. The **models** are only used by the **CardsIssuerDatabase** layer, the **RESTFul API** stuff doesn't.


#### Api Endpoints

The Scheme webhook endpoints doesn't rely directly on the *models* implemented at **cards.accouting** Django application.

The views calls directly the *Issuer service* implemented by the python module **issuer.service**.


##### Notes about the implementation

Some items were implemented in an different way than the specification:

- **HTTP 201** is used at the */authorisation* endpoint instead of **HTTP 200**. This is the default approach.
- **NO Endpoint Documentation** — As far the has 2 endpoints at the moment there is no endpoint documentation written but the parameters definitions for each endpoint it's available at **cards/api/serializers.py** that can auto generate docs based on 3rd party libraries such as *swagger*, *apidoc*.
- **Presentment Endpoint** — Despite the Scheme calls it again with the same parameters used previously on the  *authorisation endpoint* the previous used parameters are not validated or used.


## Presentment and Settlement

### On Presentment the money is moved between accounts

There is an account for **Scheme** and another for the **Issuer**, this represents the real money available at the **Issuer** on it hands and what it owns the **Scheme**.

The presentment logic is implemented within **CardsIssuerDatabase** class at **make_presentment_batch** method.

### Settlement daily task not implemented

The settlement daily task isn't implemented but changing Transaction of type authorisation old more than next day will make the task works. This can be done by just setting an Transaction to type **expired**.

The balance calculation is implemented at **cards/accounting/managers.py** file. Only a Transaction which *type/status* of **authorisation** is being summarized.


## Nice things to have

This project needs some nice features, small and major changes.

### Security layer

A public/private key signing should be a good second security layer, this layer would be applied at database level to ensure any card movement record stored over the database was stored by the service application and not *hijacked* someway.

A new **authorisation** should be double signed:
- **Issuer Service Signature** — Adds a field to the Transaction table  schema that stores a hash
that confirms this record was inserted by the service layer.
- **Scheme Signature** — Makes sure it was signed by the scheme application who called the authorisation endpoint previously and not other service.

And at the presentment should be:

1. Check if the *presentment* was really signed by the issuer service application.
2. Check if the **Scheme** calls at *presentment endpoint* previously signed this authorisation.

**ATENTION**: Maybe this approach is overthink about the security layer, but would be nice to have

### TODO

Some 'small things' not implemented but it would be cool.

* [ ] Documentation
    * [ ] api documentation
    * [x] sphinx docstring
    * [ ] output sphinx doc
* [x] tests
    * [x] coverage
    * [x] linter (flake8)

* [x] logging

* [ ] 12factor / settings outside the code base

* [ ] Docker image
    * [x] setuptools packaging

