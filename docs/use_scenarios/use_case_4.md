## Nazwa
**Konwersja przesłanej części pliku**

## Aktor główny
Worker

## Aktor pomocniczy
Serwer

## Opis
Worker otrzymuje nowy plik [`convFile`] na wewnętrzną kolejkę przetwarzania [`conversionFiles`]. Zapamiętane są adresy źródłowe [`serverData`] oraz komenda [`conversionData`], którą należy wykonać, aby skonwertować plik.

## Wyzwalacz
Otrzymanie fragmentu pliku od serwera centralnego [`receiveFile()`]

## Warunki początkowe
1. Węzeł ma połączenie z serwerem [`connectToServer()`].
2. Węzeł ma wolne miejsce w kolejce plików do konwersji [`getFreeQueueSize()`].

## Warunki końcowe
1. Węzeł odsyła plik po konwersji do centralnego serwera [`sendFile()`]

## Przepływ normalny
1. Węzeł otrzymuje komunikat z procedurą, którą należy wykonać do konwersji pliku [`conversionData`]
2. Węzeł otrzymuje część pliku przeznaczoną do konwersji [`ConvFile`]
3. Węzeł wykonuje konwersję pliku przy pomocy gotowej metody [`convertFile()`]
4. Węzeł wysyła komunikat o gotowości pliku do przesłania
5. Węzeł wysyła plik przy pomocy protokołu [`sendFile()`]

## Wyjątki
###### Nie ma połączenia z serwerem
1. System informuje użytkownika, że ze względu na błąd połączenia sieciowego nie jest w stanie przeprowadzić konwersji [`sendError()`]
2. Po upłynięciu ustalonego timeout, w którym sprawdzana jest możliwość połączenia, program kończy działanie
###### Użytkownik przerywa pracę z systemem w czasie przetwarzania
1. Następuje czyszczenie zawartości programu [`clearData()`]. Program kończy swoje działanie.
###### Błąd systemu
1. System informuje użytkownika o błędzie i prosi o ponowienie próby za kilka minut.[`sendError()`]
